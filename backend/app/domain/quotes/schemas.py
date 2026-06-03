"""
Quotes domain — Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.quotes.models import QuoteStatus


class QuoteCreateRequest(BaseModel):
    deal_id: int
    reference: Optional[str] = None
    amount: Decimal = Field(..., ge=0)
    status: QuoteStatus = QuoteStatus.DRAFT
    pdf_url: Optional[str] = None
    notes: Optional[str] = None


class QuoteUpdateRequest(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[QuoteStatus] = None
    pdf_url: Optional[str] = None
    notes: Optional[str] = None


class QuoteResponse(BaseModel):
    id: int
    deal_id: int
    reference: Optional[str] = None
    amount: float
    status: QuoteStatus
    pdf_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
