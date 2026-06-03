"""
API Router — Activities (timeline).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_internal, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.activities.models import ActivityType
from app.domain.activities.service import ActivityService
from app.domain.activities.schemas import (
    ActivityCreateRequest, ActivityUpdateRequest, ActivityResponse,
)
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=PaginatedResponse[ActivityResponse])
def list_activities(
    pagination: PaginationParams = Depends(pagination_params),
    type: ActivityType = Query(None),
    account_id: int = Query(None),
    deal_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if type:
        filters["type"] = type
    if account_id:
        filters["account_id"] = account_id
    if deal_id:
        filters["deal_id"] = deal_id
    if pagination.search:
        filters["search"] = pagination.search
    service = ActivityService(db)
    activities, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=activities, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(
    payload: ActivityCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = ActivityService(db)
    activity = service.create(payload, created_by=current_user.id)
    AuditService(db).log(current_user.id, "activity", activity.id, "create", after=activity.model_dump())
    return activity


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return ActivityService(db).get(activity_id)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    payload: ActivityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = ActivityService(db)
    before = service.get(activity_id)
    updated = service.update(activity_id, payload)
    AuditService(db).log(
        current_user.id, "activity", activity_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.delete("/{activity_id}", status_code=204)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = ActivityService(db)
    before = service.get(activity_id)
    service.delete(activity_id)
    AuditService(db).log(current_user.id, "activity", activity_id, "delete", before=before.model_dump())
