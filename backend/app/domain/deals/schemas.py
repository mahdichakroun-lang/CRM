"""
Deals domain — Schemas (DTOs).
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.deals.models import DealStage


class DealCreateRequest(BaseModel):
    account_id: int
    name: str = Field(..., min_length=1, max_length=255)
    stage: DealStage = DealStage.QUALIFICATION
    value: Optional[Decimal] = Decimal("0")
    probability: Optional[int] = Field(0, ge=0, le=100)
    expected_close_date: Optional[date] = None
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None


class DealUpdateRequest(BaseModel):
    account_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    stage: Optional[DealStage] = None
    value: Optional[Decimal] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None
    lost_reason: Optional[str] = None


class DealStageUpdateRequest(BaseModel):
    stage: DealStage
    lost_reason: Optional[str] = None  # required if stage == LOST


class DealResponse(BaseModel):
    id: int
    account_id: int
    name: str
    stage: DealStage
    value: Optional[float] = 0.0
    probability: Optional[int] = 0
    expected_close_date: Optional[date] = None
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None
    lost_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
