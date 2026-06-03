"""
Contacts domain — Repository.
"""
from typing import List
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.contacts.models import Contact


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: Session):
        super().__init__(Contact, db)

    def get_by_account(self, account_id: int, skip: int = 0, limit: int = 50) -> List[Contact]:
        return (
            self.db.query(Contact)
            .filter(Contact.account_id == account_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _apply_filters(self, query, filters):
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            from app.domain.accounts.models import Account
            query = query.outerjoin(Account, Contact.account_id == Account.id)
            query = query.filter(
                (Contact.first_name.ilike(f"%{search_val}%"))
                | (Contact.last_name.ilike(f"%{search_val}%"))
                | (Contact.email.ilike(f"%{search_val}%"))
                | (Contact.phone.ilike(f"%{search_val}%"))
                | (Account.name.ilike(f"%{search_val}%"))
            )
        for key, value in filters_copy.items():
            if value is not None and hasattr(Contact, key):
                column = getattr(Contact, key)
                if isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[Contact]:
        query = self._apply_filters(self.db.query(Contact), filters)
        if order_by and hasattr(Contact, order_by):
            query = query.order_by(getattr(Contact, order_by).desc())
        else:
            query = query.order_by(Contact.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(Contact), filters).count()
