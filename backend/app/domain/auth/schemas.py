"""
Auth domain — Pydantic schemas (DTOs).
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, field_serializer
from app.domain.auth.models import UserRole


# ── Request DTOs ──────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email_like(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    phone: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_like(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value


class AdminCreateUserRequest(BaseModel):
    """Admin can create users with any role and optional account_id."""
    name: str = Field(..., min_length=2, max_length=150)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.COMMERCIAL
    phone: Optional[str] = None
    account_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def validate_email_like(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = Field(None, min_length=3, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_like(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=128)


# ── Response DTOs ─────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    account_id: Optional[int] = None
    created_at: Any
    updated_at: Optional[Any] = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def sanitize_datetime(cls, v: Any) -> Any:
        if isinstance(v, str) and v.startswith("0000-00-00"):
            return None
        return v

    model_config = {"from_attributes": True}


class UserAssignableResponse(BaseModel):
    id: int
    name: str
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
