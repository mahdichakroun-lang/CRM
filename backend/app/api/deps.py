"""
API Dependencies — Auth, RBAC, pagination helpers.
Used by all routers via Depends().
"""
from typing import List
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.shared.security import decode_access_token
from app.shared.exceptions import UnauthorizedException, ForbiddenException
from app.domain.auth.models import User, UserRole
from app.shared.pagination import PaginationParams

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT and return the current user."""
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException()

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException()

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or deactivated")
    return user


def require_roles(*roles: UserRole):
    """
    Dependency factory: raises 403 if user's role is not in the allowed list.
    Usage: Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Role '{current_user.role.value}' is not authorized. Required: {[r.value for r in roles]}"
            )
        return current_user
    return checker


def require_internal(current_user: User = Depends(get_current_user)) -> User:
    """Block CLIENT role from accessing internal CRM resources."""
    if current_user.role == UserRole.CLIENT:
        raise ForbiddenException("Access reserved for internal users")
    return current_user


def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=1000, description="Items per page"),
    search: str = Query(None, description="Search query"),
) -> PaginationParams:
    return PaginationParams(page=page, size=size, search=search)
