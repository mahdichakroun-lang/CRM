"""
Tickets domain — Schemas (DTOs).
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field
from app.domain.tickets.models import TicketPriority, TicketStatus, TicketCategory


# ── Ticket Messages ──────────────────────────────────────
class TicketMessageCreateRequest(BaseModel):
    message: str = Field(..., min_length=1)
    is_internal: bool = False  # True = internal note, False = public reply


class TicketMessageResponse(BaseModel):
    id: int
    ticket_id: int
    author_user_id: int
    message: str
    is_internal: bool
    created_at: datetime
    author_name: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_message(cls, message) -> "TicketMessageResponse":
        return cls(
            id=message.id,
            ticket_id=message.ticket_id,
            author_user_id=message.author_user_id,
            message=message.message,
            is_internal=bool(message.is_internal),
            created_at=message.created_at,
            author_name=getattr(getattr(message, "author", None), "name", None),
        )


# ── Tickets ──────────────────────────────────────────────
class TicketCreateRequest(BaseModel):
    account_id: int
    contact_id: Optional[int] = None
    subject: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: TicketCategory = TicketCategory.SUPPORT
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TicketUpdateRequest(BaseModel):
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TicketResponse(BaseModel):
    id: int
    account_id: int
    contact_id: Optional[int] = None
    subject: str
    description: Optional[str] = None
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    assigned_to: Optional[int] = None
    created_by: int
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_overdue: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_ticket(cls, ticket) -> "TicketResponse":
        """Build response with computed is_overdue field."""
        resp = cls.model_validate(ticket)
        if (
            ticket.due_date
            and ticket.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED)
        ):
            # Normalize due_date to UTC before comparison to avoid naive/aware errors.
            due_date = ticket.due_date
            if due_date.tzinfo is None or due_date.tzinfo.utcoffset(due_date) is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            else:
                due_date = due_date.astimezone(timezone.utc)
            if datetime.now(timezone.utc) > due_date:
                resp.is_overdue = True
        return resp
