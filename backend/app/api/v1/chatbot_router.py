"""
API Router - Chatbot RAG (Client Portal).
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.domain.auth.models import User
from app.rag.config import GROQ_API_KEY
from app.rag.llm_client import LLMServiceError
from app.rag.rag_chain import ask, get_status
from app.rag.vector_store import search

router = APIRouter(prefix="/chatbot", tags=["Chatbot IA"])
logger = logging.getLogger("chatbot")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatSource(BaseModel):
    source: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = []
    chunks_used: int = 0


class ChatStatusResponse(BaseModel):
    status: str
    total_chunks: int = 0
    collection: str = ""
    llm_configured: bool = False
    error: Optional[str] = None


def _safe_search(query: str, top_k: int = 5) -> List[dict]:
    try:
        return search(query, top_k=top_k)
    except Exception:
        logger.exception("Fallback retrieval failed")
        return []


def _to_sources(chunks: List[dict]) -> List[ChatSource]:
    sources: List[ChatSource] = []
    seen: set[str] = set()
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        if source in seen:
            continue
        seen.add(source)
        sources.append(
            ChatSource(
                source=source,
                similarity=float(chunk.get("similarity", 0.0)),
            )
        )
    return sources


def _snippet(text: str, max_len: int = 260) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_len:
        return clean
    return clean[:max_len].rstrip() + "..."


def _fallback_answer(chunks: List[dict]) -> str:
    if not chunks:
        return (
            "Je peux vous aider sur FRS (services, support, devis, tickets et informations entreprise). "
            "Pouvez-vous reformuler votre question avec plus de details ?"
        )

    lines = ["Voici les informations les plus pertinentes de notre base FRS :"]
    for idx, chunk in enumerate(chunks[:3], start=1):
        lines.append(f"{idx}. {_snippet(str(chunk.get('text', '')))}")
    lines.append("")
    lines.append("Si vous voulez, je peux approfondir un point precis.")
    return "\n".join(lines)


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the FRS AI assistant.
    This endpoint is intentionally resilient and always returns a valid ChatResponse.
    """
    if not GROQ_API_KEY:
        chunks = _safe_search(payload.message, top_k=5)
        return ChatResponse(
            answer=_fallback_answer(chunks),
            sources=_to_sources(chunks),
            chunks_used=len(chunks),
        )

    try:
        result = ask(payload.message)
        return ChatResponse(
            answer=result["answer"],
            sources=[ChatSource(**s) for s in result["sources"]],
            chunks_used=result["chunks_used"],
        )
    except LLMServiceError as exc:
        logger.warning(
            "Provider soft-fail status=%s retry_after=%s provider_message=%s",
            exc.status_code,
            exc.retry_after,
            exc.provider_message,
        )
        chunks = _safe_search(payload.message, top_k=5)
        return ChatResponse(
            answer=_fallback_answer(chunks),
            sources=_to_sources(chunks),
            chunks_used=len(chunks),
        )
    except Exception:
        logger.exception("Unexpected chatbot error, serving fallback response")
        chunks = _safe_search(payload.message, top_k=5)
        return ChatResponse(
            answer=_fallback_answer(chunks),
            sources=_to_sources(chunks),
            chunks_used=len(chunks),
        )


@router.get("/status", response_model=ChatStatusResponse)
def chatbot_status(
    current_user: User = Depends(get_current_user),
):
    """Get the current status of the RAG chatbot system."""
    rag_status = get_status()
    return ChatStatusResponse(
        status=rag_status.get("status", "unknown"),
        total_chunks=rag_status.get("total_chunks", 0),
        collection=rag_status.get("collection", ""),
        llm_configured=bool(GROQ_API_KEY),
        error=rag_status.get("error"),
    )
