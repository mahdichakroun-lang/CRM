"""
API Router — Leads (with conversion endpoint).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_roles, require_internal, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.leads.models import LeadSource, LeadStatus
from app.domain.leads.service import LeadService
from app.domain.leads.schemas import (
    LeadCreateRequest, LeadUpdateRequest, LeadConvertRequest,
    LeadResponse, LeadConvertResponse,
)
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=PaginatedResponse[LeadResponse])
def list_leads(
    pagination: PaginationParams = Depends(pagination_params),
    status: LeadStatus = Query(None),
    source: LeadSource = Query(None),
    owner_user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if status:
        filters["status"] = status
    if source:
        filters["source"] = source
    if owner_user_id:
        filters["owner_user_id"] = owner_user_id
    if pagination.search:
        filters["search"] = pagination.search
    service = LeadService(db)
    leads, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=leads, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(
    payload: LeadCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = LeadService(db)
    lead = service.create(payload)
    AuditService(db).log(current_user.id, "lead", lead.id, "create", after=lead.model_dump())
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return LeadService(db).get(lead_id)


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    payload: LeadUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = LeadService(db)
    before = service.get(lead_id)
    updated = service.update(lead_id, payload)
    AuditService(db).log(
        current_user.id, "lead", lead_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.delete("/{lead_id}", status_code=204)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = LeadService(db)
    before = service.get(lead_id)
    service.delete(lead_id)
    AuditService(db).log(current_user.id, "lead", lead_id, "delete", before=before.model_dump())


@router.post("/{lead_id}/convert", response_model=LeadConvertResponse)
def convert_lead(
    lead_id: int,
    payload: LeadConvertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.COMMERCIAL, UserRole.MANAGER)),
):
    """Convert a qualified lead into Account + Contact + Deal."""
    service = LeadService(db)
    result = service.convert(lead_id, payload)
    AuditService(db).log(
        current_user.id, "lead", lead_id, "convert",
        description=f"Converted to account={result.account_id}, deal={result.deal_id}",
    )
    return result
