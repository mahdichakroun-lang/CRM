"""
Activities domain — Schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.activities.models import ActivityType


class ActivityCreateRequest(BaseModel):
    type: ActivityType
    subject: str = Field(..., min_length=1, max_length=255)
    note: Optional[str] = None
    due_date: Optional[datetime] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None


class ActivityUpdateRequest(BaseModel):
    type: Optional[ActivityType] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    note: Optional[str] = None
    due_date: Optional[datetime] = None


class ActivityResponse(BaseModel):
    id: int
    type: ActivityType
    subject: str
    note: Optional[str] = None
    due_date: Optional[datetime] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
