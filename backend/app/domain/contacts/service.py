"""
Contacts domain — Service.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.contacts.repository import ContactRepository
from app.domain.contacts.schemas import (
    ContactCreateRequest, ContactUpdateRequest, ContactResponse,
)
from app.shared.exceptions import NotFoundException


class ContactService:
    def __init__(self, db: Session):
        self.repo = ContactRepository(db)

    def create(self, payload: ContactCreateRequest) -> ContactResponse:
        data = payload.model_dump(exclude_unset=True)
        contact = self.repo.create(data)
        return ContactResponse.model_validate(contact)

    def get(self, contact_id: int) -> ContactResponse:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundException("Contact", contact_id)
        return ContactResponse.model_validate(contact)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[ContactResponse], int]:
        contacts = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [ContactResponse.model_validate(c) for c in contacts], total

    def get_by_account(self, account_id: int) -> List[ContactResponse]:
        contacts = self.repo.get_by_account(account_id)
        return [ContactResponse.model_validate(c) for c in contacts]

    def update(self, contact_id: int, payload: ContactUpdateRequest) -> ContactResponse:
        data = payload.model_dump(exclude_unset=True)
        contact = self.repo.update(contact_id, data)
        if not contact:
            raise NotFoundException("Contact", contact_id)
        return ContactResponse.model_validate(contact)

    def delete(self, contact_id: int) -> None:
        db = self.repo.db
        from app.domain.activities.models import Activity
        from app.domain.tickets.models import Ticket
        # Cascade: clear contact references (SET NULL to match FK ondelete)
        db.query(Activity).filter(Activity.contact_id == contact_id).update(
            {"contact_id": None}, synchronize_session=False
        )
        db.query(Ticket).filter(Ticket.contact_id == contact_id).update(
            {"contact_id": None}, synchronize_session=False
        )
        db.flush()
        if not self.repo.delete(contact_id):
            raise NotFoundException("Contact", contact_id)
