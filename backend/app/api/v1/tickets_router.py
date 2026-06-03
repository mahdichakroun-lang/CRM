"""
API Router — Tickets (Helpdesk).
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_roles, require_internal, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.tickets.models import TicketStatus, TicketPriority
from app.domain.tickets.service import TicketService
from app.domain.tickets.schemas import (
    TicketCreateRequest, TicketUpdateRequest, TicketResponse,
    TicketMessageCreateRequest, TicketMessageResponse,
)
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse
from app.shared.email_service import notify_ticket_status_change, notify_ticket_new_message
from app.shared.email_helpers import get_client_email_for_ticket, get_ticket_subject
from typing import List

logger = logging.getLogger("crm.tickets")

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=PaginatedResponse[TicketResponse])
def list_tickets(
    pagination: PaginationParams = Depends(pagination_params),
    status: TicketStatus = Query(None),
    priority: TicketPriority = Query(None),
    assigned_to: int = Query(None),
    account_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if assigned_to:
        filters["assigned_to"] = assigned_to
    if account_id:
        filters["account_id"] = account_id
    if pagination.search:
        filters["search"] = pagination.search
    service = TicketService(db)
    tickets, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=tickets, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.SUPPORT, UserRole.MANAGER)
    ),
):
    service = TicketService(db)
    ticket = service.create(payload, created_by=current_user.id)
    AuditService(db).log(current_user.id, "ticket", ticket.id, "create", after=ticket.model_dump())
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return TicketService(db).get(ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = TicketService(db)
    before = service.get(ticket_id)
    updated = service.update(ticket_id, payload)
    AuditService(db).log(
        current_user.id, "ticket", ticket_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )

    # 📧 Email notification on status change
    if payload.status and payload.status.value != before.status.value:
        try:
            recipient = get_client_email_for_ticket(db, ticket_id)
            if recipient:
                email, name = recipient
                notify_ticket_status_change(
                    to_email=email,
                    client_name=name,
                    ticket_id=ticket_id,
                    ticket_subject=updated.subject,
                    old_status=before.status.value,
                    new_status=updated.status.value,
                )
        except Exception as e:
            logger.warning(f"📧 Notification email échouée pour ticket #{ticket_id}: {e}")

    return updated


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    service = TicketService(db)
    before = service.get(ticket_id)
    service.delete(ticket_id)
    AuditService(db).log(current_user.id, "ticket", ticket_id, "delete", before=before.model_dump())


# ── Ticket Messages ──
@router.get("/{ticket_id}/messages", response_model=List[TicketMessageResponse])
def get_ticket_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return TicketService(db).get_messages(ticket_id)


@router.post("/{ticket_id}/messages", response_model=TicketMessageResponse, status_code=201)
def add_ticket_message(
    ticket_id: int,
    payload: TicketMessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = TicketService(db)
    msg = service.add_message(ticket_id, payload, author_id=current_user.id)
    AuditService(db).log(
        current_user.id, "ticket", ticket_id, "add_message",
        description=f"Message added to ticket #{ticket_id}",
    )

    # 📧 Email notification for public messages (not internal notes)
    if not payload.is_internal and current_user.role != UserRole.CLIENT:
        try:
            recipient = get_client_email_for_ticket(db, ticket_id)
            if recipient:
                email, name = recipient
                ticket_subj = get_ticket_subject(db, ticket_id)
                notify_ticket_new_message(
                    to_email=email,
                    client_name=name,
                    ticket_id=ticket_id,
                    ticket_subject=ticket_subj,
                    agent_name=current_user.name,
                    message_preview=payload.message,
                )
        except Exception as e:
            logger.warning(f"📧 Notification email échouée pour message ticket #{ticket_id}: {e}")

    return msg
