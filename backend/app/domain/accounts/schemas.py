"""
Accounts domain — Pydantic schemas (DTOs).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sector: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    owner_user_id: Optional[int] = None


class AccountUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    owner_user_id: Optional[int] = None


class OwnerBrief(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


class AccountResponse(BaseModel):
    id: int
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    owner_user_id: Optional[int] = None
    owner: Optional[OwnerBrief] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
