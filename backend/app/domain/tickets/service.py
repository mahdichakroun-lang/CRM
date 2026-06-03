"""
Tickets domain — Service.
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.tickets.repository import TicketRepository, TicketMessageRepository
from app.domain.tickets.models import TicketStatus, TicketMessage
from app.domain.tickets.schemas import (
    TicketCreateRequest, TicketUpdateRequest, TicketResponse,
    TicketMessageCreateRequest, TicketMessageResponse,
)
from app.shared.exceptions import NotFoundException


class TicketService:
    def __init__(self, db: Session):
        self.repo = TicketRepository(db)
        self.msg_repo = TicketMessageRepository(db)
        self.db = db

    def create(self, payload: TicketCreateRequest, created_by: int) -> TicketResponse:
        data = payload.model_dump(exclude_unset=True)
        data["created_by"] = created_by
        data["status"] = TicketStatus.OPEN
        ticket = self.repo.create(data)
        return TicketResponse.from_ticket(ticket)

    def get(self, ticket_id: int) -> TicketResponse:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket", ticket_id)
        return TicketResponse.from_ticket(ticket)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[TicketResponse], int]:
        tickets = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [TicketResponse.from_ticket(t) for t in tickets], total

    def update(self, ticket_id: int, payload: TicketUpdateRequest) -> TicketResponse:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket", ticket_id)

        data = payload.model_dump(exclude_unset=True)

        # Auto-set resolved_at when status changes to RESOLVED or CLOSED
        if payload.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED) and not ticket.resolved_at:
            data["resolved_at"] = datetime.now(timezone.utc)
        # Clear resolved_at if reopened (back to open/in_progress/waiting)
        elif payload.status and payload.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            if ticket.resolved_at:
                data["resolved_at"] = None

        updated = self.repo.update(ticket_id, data)
        return TicketResponse.from_ticket(updated)

    def delete(self, ticket_id: int) -> None:
        # Delete associated messages first (FK constraint)
        self.msg_repo.db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).delete()
        self.msg_repo.db.flush()
        if not self.repo.delete(ticket_id):
            raise NotFoundException("Ticket", ticket_id)

    # ── Messages ──────────────────────────────────────────
    def add_message(
        self, ticket_id: int, payload: TicketMessageCreateRequest, author_id: int
    ) -> TicketMessageResponse:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket", ticket_id)

        msg = self.msg_repo.create({
            "ticket_id": ticket_id,
            "author_user_id": author_id,
            "message": payload.message,
            "is_internal": payload.is_internal,
        })
        return TicketMessageResponse.from_message(msg)

    def get_messages(self, ticket_id: int) -> List[TicketMessageResponse]:
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket", ticket_id)
        messages = self.msg_repo.get_by_ticket(ticket_id)
        return [TicketMessageResponse.from_message(message) for message in messages]
