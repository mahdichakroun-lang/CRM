"""
Activities domain — Repository.
"""
import enum
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.activities.models import Activity


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: Session):
        super().__init__(Activity, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Activities."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            query = query.filter(
                (Activity.subject.ilike(f"%{search_val}%"))
                | (Activity.note.ilike(f"%{search_val}%"))
            )
        for key, value in filters_copy.items():
            if value is not None and hasattr(Activity, key):
                column = getattr(Activity, key)
                if isinstance(value, enum.Enum):
                    query = query.filter(column == value)
                elif isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Activity]:
        query = self._apply_filters(self.db.query(Activity), filters)
        if order_by and hasattr(Activity, order_by):
            query = query.order_by(getattr(Activity, order_by).desc())
        else:
            query = query.order_by(Activity.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Activity), filters).count()

    def get_by_account(self, account_id: int, skip: int = 0, limit: int = 50) -> List[Activity]:
        return (
            self.db.query(Activity)
            .filter(Activity.account_id == account_id)
            .order_by(Activity.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_by_deal(self, deal_id: int, skip: int = 0, limit: int = 50) -> List[Activity]:
        return (
            self.db.query(Activity)
            .filter(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_by_contact(self, contact_id: int, skip: int = 0, limit: int = 50) -> List[Activity]:
        return (
            self.db.query(Activity)
            .filter(Activity.contact_id == contact_id)
            .order_by(Activity.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_by_creator(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Activity]:
        return (
            self.db.query(Activity)
            .filter(Activity.created_by == user_id)
            .order_by(Activity.created_at.desc())
            .offset(skip).limit(limit).all()
        )
