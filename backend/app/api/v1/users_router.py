"""
API Router — Users (CRUD by admin).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.auth.service import AuthService
from app.domain.auth.schemas import (
    UserResponse, UserAssignableResponse, UserUpdateRequest, ChangePasswordRequest, AdminCreateUserRequest,
)
from app.shared.pagination import PaginationParams, PaginatedResponse
from app.shared.exceptions import ForbiddenException

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Create a new user (admin only). Allows setting role and account_id."""
    service = AuthService(db)
    return service.admin_create_user(payload)


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    pagination: PaginationParams = Depends(pagination_params),
    role: UserRole = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = AuthService(db)
    filters = {}
    if role:
        filters["role"] = role
    if pagination.search:
        filters["search"] = pagination.search
    users, total = service.list_users(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=users, total=total, page=pagination.page, size=pagination.size)


@router.get("/assignable", response_model=list[UserAssignableResponse])
def list_assignable_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active users who can be assigned to tickets."""
    if current_user.role == UserRole.CLIENT:
        raise ForbiddenException("Access reserved for internal users")
    return AuthService(db).list_assignable_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise ForbiddenException("You can only view your own user profile")
    service = AuthService(db)
    return service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    service = AuthService(db)
    return service.update_user(user_id, payload)


@router.post("/{user_id}/change-password", status_code=204)
def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise ForbiddenException("You can only change your own password from this endpoint")
    service = AuthService(db)
    service.change_password(user_id, payload)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    service = AuthService(db)
    service.delete_user(user_id)
