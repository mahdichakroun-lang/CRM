"""
Quotes domain — Repository.
"""
import enum
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.quotes.models import Quote


class QuoteRepository(BaseRepository[Quote]):
    def __init__(self, db: Session):
        super().__init__(Quote, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Quotes."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            from app.domain.deals.models import Deal
            from app.domain.accounts.models import Account
            from app.domain.quotes.models import QuoteStatus
            from sqlalchemy import or_
            query = query.outerjoin(Deal, Quote.deal_id == Deal.id)
            query = query.outerjoin(Account, Deal.account_id == Account.id)
            conditions = [
                Quote.reference.ilike(f"%{search_val}%"),
                Quote.notes.ilike(f"%{search_val}%"),
                Deal.name.ilike(f"%{search_val}%"),
                Account.name.ilike(f"%{search_val}%"),
            ]
            # Allow searching by status name (e.g. "draft", "accepted")
            try:
                matched_status = QuoteStatus(search_val.lower())
                conditions.append(Quote.status == matched_status)
            except ValueError:
                pass
            query = query.filter(or_(*conditions))
        for key, value in filters_copy.items():
            if value is not None and hasattr(Quote, key):
                column = getattr(Quote, key)
                if isinstance(value, enum.Enum):
                    query = query.filter(column == value)
                elif isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Quote]:
        query = self._apply_filters(self.db.query(Quote), filters)
        if order_by and hasattr(Quote, order_by):
            query = query.order_by(getattr(Quote, order_by).desc())
        else:
            query = query.order_by(Quote.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Quote), filters).count()

    def get_by_deal(self, deal_id: int) -> List[Quote]:
        return self.db.query(Quote).filter(Quote.deal_id == deal_id).all()
