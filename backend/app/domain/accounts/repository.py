"""
Accounts domain — Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.accounts.models import Account


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: Session):
        super().__init__(Account, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Accounts."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            query = query.filter(
                (Account.name.ilike(f"%{search_val}%"))
                | (Account.email.ilike(f"%{search_val}%"))
                | (Account.phone.ilike(f"%{search_val}%"))
                | (Account.city.ilike(f"%{search_val}%"))
                | (Account.sector.ilike(f"%{search_val}%"))
            )
        for key, value in filters_copy.items():
            if value is not None and hasattr(Account, key):
                column = getattr(Account, key)
                if isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Account]:
        query = self._apply_filters(self.db.query(Account), filters)
        if order_by and hasattr(Account, order_by):
            query = query.order_by(getattr(Account, order_by).desc())
        else:
            query = query.order_by(Account.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Account), filters).count()

    def search_by_name(self, name: str, skip: int = 0, limit: int = 20):
        return (
            self.db.query(Account)
            .filter(Account.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
