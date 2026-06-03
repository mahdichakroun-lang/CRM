"""
API Router — Deals (pipeline).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_internal, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.deals.models import DealStage
from app.domain.deals.service import DealService
from app.domain.deals.schemas import (
    DealCreateRequest, DealUpdateRequest, DealStageUpdateRequest, DealResponse,
)
from app.domain.activities.service import ActivityService
from app.domain.activities.schemas import ActivityResponse
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse
from typing import List

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=PaginatedResponse[DealResponse])
def list_deals(
    pagination: PaginationParams = Depends(pagination_params),
    stage: DealStage = Query(None),
    account_id: int = Query(None),
    owner_user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if stage:
        filters["stage"] = stage
    if account_id:
        filters["account_id"] = account_id
    if owner_user_id:
        filters["owner_user_id"] = owner_user_id
    if pagination.search:
        filters["search"] = pagination.search
    service = DealService(db)
    deals, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=deals, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=DealResponse, status_code=201)
def create_deal(
    payload: DealCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = DealService(db)
    deal = service.create(payload)
    AuditService(db).log(current_user.id, "deal", deal.id, "create", after=deal.model_dump())
    return deal


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return DealService(db).get(deal_id)


@router.patch("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    payload: DealUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = DealService(db)
    before = service.get(deal_id)
    updated = service.update(deal_id, payload)
    AuditService(db).log(
        current_user.id, "deal", deal_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.patch("/{deal_id}/stage", response_model=DealResponse)
def update_deal_stage(
    deal_id: int,
    payload: DealStageUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    """Move a deal through the pipeline stages."""
    service = DealService(db)
    before = service.get(deal_id)
    updated = service.update_stage(deal_id, payload)
    AuditService(db).log(
        current_user.id, "deal", deal_id, "stage_change",
        before={"stage": before.stage.value},
        after={"stage": updated.stage.value},
        description=f"Stage changed: {before.stage.value} → {updated.stage.value}",
    )
    return updated


@router.delete("/{deal_id}", status_code=204)
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = DealService(db)
    before = service.get(deal_id)
    service.delete(deal_id)
    AuditService(db).log(current_user.id, "deal", deal_id, "delete", before=before.model_dump())


# ── Nested: Activities under Deal ──
@router.get("/{deal_id}/activities", response_model=List[ActivityResponse])
def get_deal_activities(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return ActivityService(db).get_by_deal(deal_id)
