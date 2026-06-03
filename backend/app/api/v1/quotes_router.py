"""
API Router — Quotes (devis).
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_internal, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.quotes.service import QuoteService
from app.domain.quotes.schemas import (
    QuoteCreateRequest, QuoteUpdateRequest, QuoteResponse,
)
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse
from app.shared.email_service import notify_new_quote
from app.shared.email_helpers import get_client_email_for_quote
from app.domain.deals.models import Deal
from typing import List

logger = logging.getLogger("crm.quotes")

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.get("", response_model=PaginatedResponse[QuoteResponse])
def list_quotes(
    pagination: PaginationParams = Depends(pagination_params),
    deal_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if deal_id:
        filters["deal_id"] = deal_id
    if pagination.search:
        filters["search"] = pagination.search
    service = QuoteService(db)
    quotes, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=quotes, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=QuoteResponse, status_code=201)
def create_quote(
    payload: QuoteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = QuoteService(db)
    quote = service.create(payload)
    AuditService(db).log(current_user.id, "quote", quote.id, "create", after=quote.model_dump())

    # 📧 Email notification for new quote
    try:
        recipient = get_client_email_for_quote(db, payload.deal_id)
        if recipient:
            email, name = recipient
            deal = db.query(Deal).filter(Deal.id == payload.deal_id).first()
            deal_name = deal.name if deal else "N/A"
            notify_new_quote(
                to_email=email,
                client_name=name,
                quote_reference=quote.reference or f"DEV-{quote.id}",
                quote_amount=quote.amount,
                deal_name=deal_name,
            )
    except Exception as e:
        logger.warning(f"📧 Notification email échouée pour devis #{quote.id}: {e}")

    return quote


@router.get("/{quote_id}", response_model=QuoteResponse)
def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return QuoteService(db).get(quote_id)


@router.patch("/{quote_id}", response_model=QuoteResponse)
def update_quote(
    quote_id: int,
    payload: QuoteUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = QuoteService(db)
    before = service.get(quote_id)
    updated = service.update(quote_id, payload)
    AuditService(db).log(
        current_user.id, "quote", quote_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.delete("/{quote_id}", status_code=204)
def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = QuoteService(db)
    before = service.get(quote_id)
    service.delete(quote_id)
    AuditService(db).log(current_user.id, "quote", quote_id, "delete", before=before.model_dump())
