"""
Tickets domain — Repository.
"""
import enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.tickets.models import Ticket, TicketMessage, TicketStatus, TicketPriority


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: Session):
        super().__init__(Ticket, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Tickets."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            conditions = [
                Ticket.subject.ilike(f"%{search_val}%"),
                Ticket.description.ilike(f"%{search_val}%"),
            ]
            # Allow searching by status (e.g. "open", "resolved")
            try:
                matched_status = TicketStatus(search_val.lower())
                conditions.append(Ticket.status == matched_status)
            except ValueError:
                pass
            # Allow searching by priority (e.g. "urgent", "high")
            try:
                matched_priority = TicketPriority(search_val.lower())
                conditions.append(Ticket.priority == matched_priority)
            except ValueError:
                pass

            from sqlalchemy import or_
            query = query.filter(or_(*conditions))
        for key, value in filters_copy.items():
            if value is not None and hasattr(Ticket, key):
                column = getattr(Ticket, key)
                if isinstance(value, enum.Enum):
                    query = query.filter(column == value)
                elif isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Ticket]:
        query = self._apply_filters(self.db.query(Ticket), filters)
        if order_by and hasattr(Ticket, order_by):
            query = query.order_by(getattr(Ticket, order_by).desc())
        else:
            query = query.order_by(Ticket.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Ticket), filters).count()

    def get_by_account(self, account_id: int) -> List[Ticket]:
        return (
            self.db.query(Ticket)
            .filter(Ticket.account_id == account_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    def get_by_assignee(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Ticket]:
        return (
            self.db.query(Ticket)
            .filter(Ticket.assigned_to == user_id)
            .order_by(Ticket.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def count_open(self) -> int:
        return (
            self.db.query(Ticket)
            .filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .count()
        )

    def count_overdue(self) -> int:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Ticket)
            .filter(
                Ticket.due_date < now,
                Ticket.status.notin_([TicketStatus.RESOLVED, TicketStatus.CLOSED]),
            )
            .count()
        )

    def avg_resolution_hours(self) -> float:
        """Average resolution time in hours for resolved/closed tickets."""
        resolved_tickets = (
            self.db.query(Ticket.created_at, Ticket.resolved_at)
            .filter(Ticket.resolved_at.isnot(None))
            .all()
        )
        if not resolved_tickets:
            return 0.0

        durations = []
        for created_at, resolved_at in resolved_tickets:
            if not created_at or not resolved_at:
                continue
            delta = resolved_at - created_at
            durations.append(delta.total_seconds() / 3600)

        if not durations:
            return 0.0
        return round(sum(durations) / len(durations), 1)

    def count_by_status(self) -> list:
        return (
            self.db.query(Ticket.status, func.count(Ticket.id))
            .group_by(Ticket.status)
            .all()
        )

    def count_by_priority(self) -> list:
        return (
            self.db.query(Ticket.priority, func.count(Ticket.id))
            .group_by(Ticket.priority)
            .all()
        )


class TicketMessageRepository(BaseRepository[TicketMessage]):
    def __init__(self, db: Session):
        super().__init__(TicketMessage, db)

    def get_by_ticket(self, ticket_id: int) -> List[TicketMessage]:
        return (
            self.db.query(TicketMessage)
            .filter(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at.asc())
            .all()
        )
