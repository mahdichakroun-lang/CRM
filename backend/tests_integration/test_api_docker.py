"""
Integration tests against a live backend container.

Run inside Docker:
    pytest -q tests_integration
"""
from __future__ import annotations

import os
import time
from typing import Any, Iterable

import httpx
import pytest


BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://backend:8000/api/v1")
HEALTH_URL = os.getenv("INTEGRATION_HEALTH_URL", "http://backend:8000/health")


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    expected: Iterable[int] = (200,),
    token: str | None = None,
    payload: dict[str, Any] | None = None,
) -> httpx.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.request(method, path, headers=headers, json=payload)
    assert response.status_code in expected, (
        f"{method} {path} expected {tuple(expected)}, "
        f"got {response.status_code}: {response.text}"
    )
    return response


def _json(response: httpx.Response) -> dict[str, Any]:
    return response.json()


def _login(client: httpx.Client, email: str, password: str) -> str:
    response = _request(
        client,
        "POST",
        "/auth/login",
        payload={"email": email, "password": password},
    )
    return _json(response)["access_token"]


def _wait_backend_ready() -> None:
    with httpx.Client(timeout=5.0) as client:
        for _ in range(40):
            try:
                response = client.get(HEALTH_URL)
                if response.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(1)
    raise AssertionError(f"Backend health check failed at {HEALTH_URL}")


@pytest.mark.integration
def test_full_docker_api_flow() -> None:
    _wait_backend_ready()

    ids: dict[str, int | None] = {
        "account": None,
        "contact": None,
        "deal": None,
        "activity": None,
        "quote": None,
        "ticket": None,
        "lead": None,
        "conv_account": None,
        "conv_contact": None,
        "conv_deal": None,
        "client_ticket": None,
    }
    temp: dict[str, int | None] = {
        "tmp_user": None,
        "client_user": None,
    }

    with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
        admin_token = _login(client, "admin@crm.com", "admin123")
        commercial_token = _login(client, "ahmed@crm.com", "ahmed123")
        support_token = _login(client, "omar@crm.com", "omar1234")
        manager_token = _login(client, "fatima@crm.com", "fatima123")

        # RBAC quick checks
        _request(client, "GET", "/users", token=admin_token, expected=(200,))
        _request(client, "GET", "/users", token=manager_token, expected=(200,))
        _request(client, "GET", "/users", token=commercial_token, expected=(403,))
        _request(client, "GET", "/users", token=support_token, expected=(403,))
        _request(client, "GET", "/reports/sales", token=commercial_token, expected=(200,))
        _request(client, "GET", "/reports/support", token=support_token, expected=(200,))
        _request(client, "GET", "/reports/audit-logs", token=manager_token, expected=(200,))

        try:
            # Accounts / Contacts
            account = _request(
                client,
                "POST",
                "/accounts",
                token=admin_token,
                expected=(201,),
                payload={
                    "name": _unique("INT_ACC"),
                    "sector": "IT",
                    "city": "Paris",
                },
            )
            ids["account"] = _json(account)["id"]
            _request(client, "PATCH", f"/accounts/{ids['account']}", token=admin_token, payload={"city": "Lyon"})
            _request(client, "GET", f"/accounts/{ids['account']}", token=admin_token)

            contact = _request(
                client,
                "POST",
                "/contacts",
                token=admin_token,
                expected=(201,),
                payload={
                    "account_id": ids["account"],
                    "first_name": "Int",
                    "last_name": "Contact",
                    "email": f"{_unique('contact')}@crm.local",
                },
            )
            ids["contact"] = _json(contact)["id"]
            _request(client, "PATCH", f"/contacts/{ids['contact']}", token=admin_token, payload={"position": "CTO"})

            # Deals / Activities / Quotes
            deal = _request(
                client,
                "POST",
                "/deals",
                token=admin_token,
                expected=(201,),
                payload={
                    "account_id": ids["account"],
                    "name": _unique("INT_DEAL"),
                    "value": 100000,
                    "probability": 40,
                },
            )
            ids["deal"] = _json(deal)["id"]
            _request(
                client,
                "PATCH",
                f"/deals/{ids['deal']}/stage",
                token=admin_token,
                payload={"stage": "proposal"},
            )
            _request(client, "GET", f"/deals/{ids['deal']}", token=admin_token)

            activity = _request(
                client,
                "POST",
                "/activities",
                token=admin_token,
                expected=(201,),
                payload={
                    "type": "call",
                    "subject": "Integration call",
                    "account_id": ids["account"],
                    "contact_id": ids["contact"],
                    "deal_id": ids["deal"],
                },
            )
            ids["activity"] = _json(activity)["id"]
            _request(
                client,
                "PATCH",
                f"/activities/{ids['activity']}",
                token=admin_token,
                payload={"subject": "Integration call updated"},
            )

            quote = _request(
                client,
                "POST",
                "/quotes",
                token=admin_token,
                expected=(201,),
                payload={
                    "deal_id": ids["deal"],
                    "reference": _unique("INT"),
                    "amount": 120000,
                    "status": "draft",
                },
            )
            ids["quote"] = _json(quote)["id"]
            _request(client, "PATCH", f"/quotes/{ids['quote']}", token=admin_token, payload={"status": "sent"})

            # Tickets
            ticket = _request(
                client,
                "POST",
                "/tickets",
                token=admin_token,
                expected=(201,),
                payload={
                    "account_id": ids["account"],
                    "contact_id": ids["contact"],
                    "subject": _unique("INT_TICKET"),
                    "description": "integration",
                    "category": "support",
                    "priority": "medium",
                    "due_date": "2026-03-20T10:00:00Z",
                },
            )
            ids["ticket"] = _json(ticket)["id"]
            _request(client, "GET", "/tickets", token=admin_token)
            _request(client, "GET", f"/tickets/{ids['ticket']}", token=admin_token)
            _request(
                client,
                "PATCH",
                f"/tickets/{ids['ticket']}",
                token=admin_token,
                payload={"status": "in_progress"},
            )
            _request(
                client,
                "POST",
                f"/tickets/{ids['ticket']}/messages",
                token=admin_token,
                expected=(201,),
                payload={"message": "integration public", "is_internal": 0},
            )
            _request(client, "GET", f"/tickets/{ids['ticket']}/messages", token=admin_token)

            # Leads + conversion
            lead = _request(
                client,
                "POST",
                "/leads",
                token=admin_token,
                expected=(201,),
                payload={
                    "contact_name": "Lead Int",
                    "company_name": _unique("LeadCorp"),
                    "email": f"{_unique('lead')}@crm.local",
                    "source": "website",
                    "estimated_value": 50000,
                },
            )
            ids["lead"] = _json(lead)["id"]
            _request(
                client,
                "PATCH",
                f"/leads/{ids['lead']}",
                token=admin_token,
                payload={"status": "qualified"},
            )
            converted = _request(
                client,
                "POST",
                f"/leads/{ids['lead']}/convert",
                token=admin_token,
                payload={"deal_name": _unique("Converted"), "deal_value": 50000},
            )
            converted_data = _json(converted)
            ids["conv_account"] = converted_data["account_id"]
            ids["conv_contact"] = converted_data["contact_id"]
            ids["conv_deal"] = converted_data["deal_id"]

            # Nested endpoints
            _request(client, "GET", f"/accounts/{ids['account']}/contacts", token=admin_token)
            _request(client, "GET", f"/accounts/{ids['account']}/deals", token=admin_token)
            _request(client, "GET", f"/accounts/{ids['account']}/activities", token=admin_token)
            _request(client, "GET", f"/deals/{ids['deal']}/activities", token=admin_token)

            # Auth profile + password flow
            tmp_email = f"{_unique('tmp.user')}@crm.local"
            tmp_password = "TmpPass123!"
            reg_tmp = _request(
                client,
                "POST",
                "/auth/register",
                expected=(201,),
                payload={
                    "name": "Tmp User",
                    "email": tmp_email,
                    "password": tmp_password,
                    "phone": "+330000",
                },
            )
            temp["tmp_user"] = _json(reg_tmp)["id"]
            tmp_token = _login(client, tmp_email, tmp_password)
            _request(client, "GET", "/auth/me", token=tmp_token)
            _request(
                client,
                "PATCH",
                "/auth/me",
                token=tmp_token,
                payload={"name": "Tmp User Updated", "phone": "+331111"},
            )
            _request(
                client,
                "POST",
                f"/users/{temp['tmp_user']}/change-password",
                token=tmp_token,
                expected=(204,),
                payload={"old_password": tmp_password, "new_password": "TmpPass456!"},
            )
            _login(client, tmp_email, "TmpPass456!")

            # Client portal checks (requires seeded demo client)
            try:
                seeded_client_token = _login(client, "karim@sonatrach.dz", "client123")
            except AssertionError as exc:
                pytest.skip(f"Seeded client user unavailable for client portal checks: {exc}")
                return

            _request(client, "GET", "/client/dashboard", token=seeded_client_token)
            _request(client, "GET", "/client/tickets", token=seeded_client_token)
            client_ticket = _request(
                client,
                "POST",
                "/client/tickets",
                token=seeded_client_token,
                expected=(201,),
                payload={
                    "subject": _unique("CLIENT_TICKET"),
                    "description": "client integration",
                    "category": "support",
                    "priority": "low",
                },
            )
            ids["client_ticket"] = _json(client_ticket)["id"]
            _request(client, "GET", f"/client/tickets/{ids['client_ticket']}", token=seeded_client_token)
            _request(
                client,
                "POST",
                f"/tickets/{ids['client_ticket']}/messages",
                token=admin_token,
                expected=(201,),
                payload={"message": "internal note", "is_internal": 1},
            )
            _request(
                client,
                "POST",
                f"/client/tickets/{ids['client_ticket']}/messages",
                token=seeded_client_token,
                expected=(201,),
                payload={"message": "client public"},
            )
            messages = _request(
                client,
                "GET",
                f"/client/tickets/{ids['client_ticket']}/messages",
                token=seeded_client_token,
            )
            assert all(m.get("is_internal", 0) == 0 for m in messages.json()), "Client can see internal notes"
            _request(client, "GET", "/client/quotes", token=seeded_client_token)

        finally:
            if temp["tmp_user"]:
                _request(client, "DELETE", f"/users/{temp['tmp_user']}", token=admin_token, expected=(204, 404))
            if ids["client_ticket"]:
                _request(client, "DELETE", f"/tickets/{ids['client_ticket']}", token=admin_token, expected=(204, 404))
            if ids["lead"]:
                _request(client, "DELETE", f"/leads/{ids['lead']}", token=admin_token, expected=(204, 404))
            if ids["conv_deal"]:
                _request(client, "DELETE", f"/deals/{ids['conv_deal']}", token=admin_token, expected=(204, 404))
            if ids["conv_contact"]:
                _request(client, "DELETE", f"/contacts/{ids['conv_contact']}", token=admin_token, expected=(204, 404))
            if ids["conv_account"]:
                _request(client, "DELETE", f"/accounts/{ids['conv_account']}", token=admin_token, expected=(204, 404))
            if ids["quote"]:
                _request(client, "DELETE", f"/quotes/{ids['quote']}", token=admin_token, expected=(204, 404))
            if ids["activity"]:
                _request(client, "DELETE", f"/activities/{ids['activity']}", token=admin_token, expected=(204, 404))
            if ids["ticket"]:
                _request(client, "DELETE", f"/tickets/{ids['ticket']}", token=admin_token, expected=(204, 404))
            if ids["contact"]:
                _request(client, "DELETE", f"/contacts/{ids['contact']}", token=admin_token, expected=(204, 404))
            if ids["deal"]:
                _request(client, "DELETE", f"/deals/{ids['deal']}", token=admin_token, expected=(204, 404))
            if ids["account"]:
                _request(client, "DELETE", f"/accounts/{ids['account']}", token=admin_token, expected=(204, 404))
