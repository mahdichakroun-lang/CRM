"""
API Router — Contacts.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_internal, require_roles, pagination_params
from app.domain.auth.models import User, UserRole
from app.domain.contacts.service import ContactService
from app.domain.contacts.schemas import (
    ContactCreateRequest, ContactUpdateRequest, ContactResponse,
)
from app.domain.audit.service import AuditService
from app.shared.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=PaginatedResponse[ContactResponse])
def list_contacts(
    pagination: PaginationParams = Depends(pagination_params),
    account_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    filters = {}
    if account_id:
        filters["account_id"] = account_id
    if pagination.search:
        filters["search"] = pagination.search
    service = ContactService(db)
    contacts, total = service.list(skip=pagination.skip, limit=pagination.size, filters=filters)
    return PaginatedResponse.create(items=contacts, total=total, page=pagination.page, size=pagination.size)


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    payload: ContactCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = ContactService(db)
    contact = service.create(payload)
    AuditService(db).log(current_user.id, "contact", contact.id, "create", after=contact.model_dump())
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    return ContactService(db).get(contact_id)


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    payload: ContactUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    service = ContactService(db)
    before = service.get(contact_id)
    updated = service.update(contact_id, payload)
    AuditService(db).log(
        current_user.id, "contact", contact_id, "update",
        before=before.model_dump(), after=updated.model_dump(),
    )
    return updated


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = ContactService(db)
    before = service.get(contact_id)
    service.delete(contact_id)
    AuditService(db).log(current_user.id, "contact", contact_id, "delete", before=before.model_dump())
