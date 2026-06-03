"""
Auth domain — Repository (data access layer).
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.auth.models import User, UserRole


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Multi-field search + standard filters for Users."""
        if not filters:
            return query
        filters_copy = filters.copy()
        search_val = filters_copy.pop("search", None)
        if search_val:
            query = query.filter(
                (User.name.ilike(f"%{search_val}%"))
                | (User.email.ilike(f"%{search_val}%"))
            )
        for key, value in filters_copy.items():
            if value is not None and hasattr(User, key):
                column = getattr(User, key)
                if isinstance(value, str):
                    query = query.filter(column.ilike(f"%{value}%"))
                else:
                    query = query.filter(column == value)
        return query

    def get_all(self, skip: int = 0, limit: int = 20, filters: dict = None, order_by: str = None) -> List[User]:
        query = self._apply_filters(self.db.query(User), filters)
        if order_by and hasattr(User, order_by):
            query = query.order_by(getattr(User, order_by).desc())
        else:
            query = query.order_by(User.id.desc())
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict = None) -> int:
        return self._apply_filters(self.db.query(User), filters).count()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        query = self.db.query(User).filter(User.email == email)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None

    def get_active_users(self, skip: int = 0, limit: int = 20):
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_assignable_users(self) -> List[User]:
        """Users allowed to be assigned to tickets."""
        assignable_roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPPORT]
        return (
            self.db.query(User)
            .filter(User.is_active == True, User.role.in_(assignable_roles))
            .order_by(User.name.asc())
            .all()
        )
