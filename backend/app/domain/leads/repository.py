"""
Leads domain — Repository.
"""
import enum
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.leads.models import Lead, LeadStatus, LeadSource


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: Session):
        super().__init__(Lead, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Leads."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            conditions = [
                Lead.contact_name.ilike(f"%{search_val}%"),
                Lead.company_name.ilike(f"%{search_val}%"),
                Lead.email.ilike(f"%{search_val}%"),
                Lead.phone.ilike(f"%{search_val}%"),
            ]
            # Allow searching by status name (e.g. "qualified", "converted")
            try:
                matched_status = LeadStatus(search_val.lower())
                conditions.append(Lead.status == matched_status)
            except ValueError:
                pass
            # Allow searching by source name (e.g. "website", "referral")
            try:
                matched_source = LeadSource(search_val.lower())
                conditions.append(Lead.source == matched_source)
            except ValueError:
                pass
            from sqlalchemy import or_
            query = query.filter(or_(*conditions))
        for key, value in filters_copy.items():
            if value is not None and hasattr(Lead, key):
                column = getattr(Lead, key)
                if isinstance(value, enum.Enum):
                    query = query.filter(column == value)
                elif isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Lead]:
        query = self._apply_filters(self.db.query(Lead), filters)
        if order_by and hasattr(Lead, order_by):
            query = query.order_by(getattr(Lead, order_by).desc())
        else:
            query = query.order_by(Lead.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Lead), filters).count()

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 20) -> List[Lead]:
        return (
            self.db.query(Lead)
            .filter(Lead.owner_user_id == owner_id)
            .order_by(Lead.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: LeadStatus, skip: int = 0, limit: int = 20) -> List[Lead]:
        return (
            self.db.query(Lead)
            .filter(Lead.status == status)
            .order_by(Lead.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_source(self) -> list:
        """Count leads grouped by source."""
        from sqlalchemy import func
        return (
            self.db.query(Lead.source, func.count(Lead.id))
            .group_by(Lead.source)
            .all()
        )

    def count_by_status(self) -> list:
        """Count leads grouped by status."""
        from sqlalchemy import func
        return (
            self.db.query(Lead.status, func.count(Lead.id))
            .group_by(Lead.status)
            .all()
        )
