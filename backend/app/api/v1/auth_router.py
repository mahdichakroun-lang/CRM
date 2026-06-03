"""
API Router — Auth (login, register, me, profile update).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.database import get_db
from app.api.deps import get_current_user, require_roles
from app.domain.auth.models import User, UserRole
from app.domain.auth.service import AuthService
from app.domain.auth.schemas import (
    LoginRequest, RegisterRequest, ChangePasswordRequest, TokenResponse, UserResponse,
)
from app.domain.audit.service import AuditService

router = APIRouter(prefix="/auth", tags=["Auth"])


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    service = AuthService(db)
    return service.login(payload)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Register a new user (admin only). Always creates a commercial-role user."""
    service = AuthService(db)
    user = service.register(payload)
    AuditService(db).log(
        current_user.id, "user", user.id, "register",
        after=user.model_dump(),
        description=f"Admin registered new user: {payload.email}",
    )
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update own profile (name, phone). Available to all authenticated users."""
    service = AuthService(db)
    from app.domain.auth.schemas import UserUpdateRequest
    update_data = UserUpdateRequest(
        name=payload.name,
        phone=payload.phone,
    )
    return service.update_user(current_user.id, update_data)


@router.post("/me/change-password", status_code=204)
def change_own_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change own password."""
    service = AuthService(db)
    service.change_password(current_user.id, payload)
