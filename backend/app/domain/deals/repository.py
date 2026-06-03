"""
Deals domain — Repository.
"""
import enum
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.deals.models import Deal, DealStage


class DealRepository(BaseRepository[Deal]):
    def __init__(self, db: Session):
        super().__init__(Deal, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Deals."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            from app.domain.accounts.models import Account
            query = query.outerjoin(Account, Deal.account_id == Account.id)
            conditions = [
                Deal.name.ilike(f"%{search_val}%"),
                Deal.notes.ilike(f"%{search_val}%"),
                Deal.lost_reason.ilike(f"%{search_val}%"),
                Account.name.ilike(f"%{search_val}%"),
            ]
            # Allow searching by stage name (e.g. "won", "lost", "negotiation")
            try:
                matched_stage = DealStage(search_val.lower())
                conditions.append(Deal.stage == matched_stage)
            except ValueError:
                pass
            from sqlalchemy import or_
            query = query.filter(or_(*conditions))
        for key, value in filters_copy.items():
            if value is not None and hasattr(Deal, key):
                column = getattr(Deal, key)
                if isinstance(value, enum.Enum):
                    query = query.filter(column == value)
                elif isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Deal]:
        query = self._apply_filters(self.db.query(Deal), filters)
        if order_by and hasattr(Deal, order_by):
            query = query.order_by(getattr(Deal, order_by).desc())
        else:
            query = query.order_by(Deal.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Deal), filters).count()

    def get_by_account(self, account_id: int) -> List[Deal]:
        return self.db.query(Deal).filter(Deal.account_id == account_id).all()

    def get_by_stage(self, stage: DealStage, skip: int = 0, limit: int = 50) -> List[Deal]:
        return (
            self.db.query(Deal)
            .filter(Deal.stage == stage)
            .offset(skip).limit(limit).all()
        )

    def pipeline_summary(self) -> list:
        """Returns [(stage, count, total_value), ...]"""
        return (
            self.db.query(
                Deal.stage,
                func.count(Deal.id),
                func.coalesce(func.sum(Deal.value), 0),
            )
            .group_by(Deal.stage)
            .all()
        )

    def total_won_value(self):
        result = (
            self.db.query(func.coalesce(func.sum(Deal.value), 0))
            .filter(Deal.stage == DealStage.WON)
            .scalar()
        )
        from decimal import Decimal
        return Decimal(str(result)) if result else Decimal("0")
