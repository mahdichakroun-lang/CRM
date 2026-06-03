"""
Contacts domain — Schemas (DTOs).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ContactCreateRequest(BaseModel):
    account_id: int
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None


class ContactUpdateRequest(BaseModel):
    account_id: Optional[int] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    account_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
