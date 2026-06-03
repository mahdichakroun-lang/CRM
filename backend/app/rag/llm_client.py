"""
LLM Client - Interface with Groq for answer generation.
Uses Groq API with an OpenAI-compatible endpoint.
"""
from __future__ import annotations

import re
from typing import Any

import httpx

from app.rag.config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL, SYSTEM_PROMPT


class LLMServiceError(RuntimeError):
    """Known upstream/provider error mapped to an API-safe HTTP status."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 503,
        retry_after: int | None = None,
        provider_message: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        self.provider_message = provider_message


def _extract_provider_message(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None

    error_block = payload.get("error")
    if isinstance(error_block, dict):
        message = error_block.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()

    message = payload.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()

    return None


def _extract_retry_after_seconds(response: httpx.Response, payload: Any) -> int | None:
    retry_after_header = response.headers.get("Retry-After")
    if retry_after_header:
        try:
            return int(retry_after_header)
        except ValueError:
            pass

    if not isinstance(payload, dict):
        return None

    details = payload.get("error", {}).get("details")
    if not isinstance(details, list):
        return None

    for detail in details:
        if not isinstance(detail, dict):
            continue
        retry_delay = detail.get("retryDelay")
        if not isinstance(retry_delay, str):
            continue
        match = re.match(r"^(\d+)s$", retry_delay.strip())
        if match:
            return int(match.group(1))

    return None


def _raise_from_http_status(exc: httpx.HTTPStatusError) -> None:
    response = exc.response
    payload: Any = None
    provider_message = response.text.strip() or None

    try:
        payload = response.json()
    except ValueError:
        payload = None
    else:
        parsed_message = _extract_provider_message(payload)
        if parsed_message:
            provider_message = parsed_message

    retry_after = _extract_retry_after_seconds(response, payload)

    if response.status_code == 429:
        message = (
            "Le service IA est temporairement limite (quota ou rate limit). "
            "Reessayez dans quelques instants."
        )
        if retry_after:
            message += f" Delai conseille: {retry_after}s."
        raise LLMServiceError(
            message,
            status_code=429,
            retry_after=retry_after,
            provider_message=provider_message,
        )

    if response.status_code in (401, 403):
        raise LLMServiceError(
            "La cle API du service IA est invalide, expiree ou non autorisee.",
            status_code=503,
            provider_message=provider_message,
        )

    if response.status_code >= 500:
        raise LLMServiceError(
            "Le fournisseur IA est indisponible pour le moment. Reessayez plus tard.",
            status_code=503,
            provider_message=provider_message,
        )

    raise LLMServiceError(
        f"Erreur du service IA ({response.status_code}).",
        status_code=502,
        provider_message=provider_message,
    )


def generate_answer(query: str, context_chunks: list[dict]) -> str:
    """
    Generate an answer using Groq with RAG context.
    The LLM is strictly instructed to only answer about FRS.
    """
    if not GROQ_API_KEY:
        return "Le chatbot IA n'est pas encore configure. Veuillez ajouter la cle API Groq."

    # Build context from retrieved chunks
    if context_chunks:
        context_parts = []
        for chunk in context_chunks:
            context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
        context_text = "\n\n---\n\n".join(context_parts)
    else:
        context_text = "Aucun contexte pertinent trouve dans la base de connaissances."

    # Build the user prompt with context
    user_prompt = f"""## CONTEXTE (Base de connaissances FRS) :
{context_text}

## QUESTION DU CLIENT :
{query}

## INSTRUCTION :
Reponds a la question du client en utilisant UNIQUEMENT les informations du contexte ci-dessus.
Si la question ne concerne pas FRS ou si tu ne trouves pas la reponse dans le contexte, applique les regles de refus definies dans tes instructions systeme.
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_p": 0.8,
    }

    try:
        response = httpx.post(
            GROQ_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise LLMServiceError(
            "Le service IA a depasse le delai de reponse. Reessayez.",
            status_code=504,
        ) from exc
    except httpx.HTTPStatusError as exc:
        _raise_from_http_status(exc)
    except httpx.RequestError as exc:
        raise LLMServiceError(
            "Impossible de joindre le service IA. Verifiez votre connexion reseau.",
            status_code=503,
        ) from exc

    result = response.json()
    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMServiceError(
            "Le service IA a retourne une reponse inattendue.",
            status_code=502,
            provider_message=str(result)[:500],
        ) from exc
