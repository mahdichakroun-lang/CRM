"""
Leads domain — Schemas (DTOs).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.leads.models import LeadSource, LeadStatus


class LeadCreateRequest(BaseModel):
    company_name: Optional[str] = None
    contact_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    source: LeadSource = LeadSource.OTHER
    status: LeadStatus = LeadStatus.NEW
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None
    estimated_value: Optional[int] = None


class LeadUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None
    estimated_value: Optional[int] = None


class LeadConvertRequest(BaseModel):
    """Data needed to convert a lead into Account + Contact + Deal."""
    account_name: Optional[str] = None  # defaults to lead.company_name
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    deal_name: Optional[str] = None
    deal_value: Optional[int] = None
    deal_stage: str = "qualification"


class LeadResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    contact_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: LeadSource
    status: LeadStatus
    owner_user_id: Optional[int] = None
    notes: Optional[str] = None
    estimated_value: Optional[int] = None
    converted_account_id: Optional[int] = None
    converted_contact_id: Optional[int] = None
    converted_deal_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LeadConvertResponse(BaseModel):
    lead_id: int
    account_id: int
    contact_id: int
    deal_id: int
    message: str = "Lead converted successfully"
