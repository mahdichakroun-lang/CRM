"""
API Router — Accounts.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_internal, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.accounts.service import AccountService
from app.domain.accounts.schemas import (
    AccountCreateRequest, AccountUpdateRequest, AccountResponse,
)
from app.domain.contacts.service import ContactService
from app.domain.contacts.schemas import ContactResponse
from app.domain.deals.service import DealService
from app.domain.deals.schemas import DealResponse
from app.domain.activities.service import ActivityService
from app.domain.activities.schemas import ActivityResponse
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse
from typing import List

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=PaginatedResponse[AccountResponse])
def list_accounts(
    pagination: PaginationParams = Depends(pagination_params),
    sector: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if sector:
        filters["sector"] = sector
    if pagination.search:
        filters["search"] = pagination.search
    service = AccountService(db)
    accounts, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=accounts, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    payload: AccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = AccountService(db)
    account = service.create(payload)
    AuditService(db).log(current_user.id, "account", account.id, "create", after=account.model_dump())
    return account


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return AccountService(db).get(account_id)


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    payload: AccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = AccountService(db)
    before = service.get(account_id)
    updated = service.update(account_id, payload)
    AuditService(db).log(
        current_user.id, "account", account_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = AccountService(db)
    before = service.get(account_id)
    service.delete(account_id)
    AuditService(db).log(current_user.id, "account", account_id, "delete", before=before.model_dump())


# ── Nested: Contacts under Account ──
@router.get("/{account_id}/contacts", response_model=List[ContactResponse])
def get_account_contacts(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return ContactService(db).get_by_account(account_id)


# ── Nested: Deals under Account ──
@router.get("/{account_id}/deals", response_model=List[DealResponse])
def get_account_deals(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return DealService(db).get_by_account(account_id)


# ── Nested: Activities under Account ──
@router.get("/{account_id}/activities", response_model=List[ActivityResponse])
def get_account_activities(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return ActivityService(db).get_by_account(account_id)
