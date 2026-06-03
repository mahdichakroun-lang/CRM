"""
Leads domain — Service (includes conversion logic).
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.leads.repository import LeadRepository
from app.domain.leads.models import LeadStatus
from app.domain.leads.schemas import (
    LeadCreateRequest, LeadUpdateRequest, LeadConvertRequest,
    LeadResponse, LeadConvertResponse,
)
from app.domain.accounts.models import Account
from app.domain.contacts.models import Contact
from app.domain.deals.models import Deal, DealStage
from app.shared.exceptions import NotFoundException, BadRequestException


class LeadService:
    def __init__(self, db: Session):
        self.repo = LeadRepository(db)
        self.db = db

    def create(self, payload: LeadCreateRequest) -> LeadResponse:
        data = payload.model_dump(exclude_unset=True)
        lead = self.repo.create(data)
        return LeadResponse.model_validate(lead)

    def get(self, lead_id: int) -> LeadResponse:
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException("Lead", lead_id)
        return LeadResponse.model_validate(lead)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[LeadResponse], int]:
        leads = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [LeadResponse.model_validate(l) for l in leads], total

    def update(self, lead_id: int, payload: LeadUpdateRequest) -> LeadResponse:
        data = payload.model_dump(exclude_unset=True)
        lead = self.repo.update(lead_id, data)
        if not lead:
            raise NotFoundException("Lead", lead_id)
        return LeadResponse.model_validate(lead)

    def delete(self, lead_id: int) -> None:
        if not self.repo.delete(lead_id):
            raise NotFoundException("Lead", lead_id)

    def convert(self, lead_id: int, payload: LeadConvertRequest) -> LeadConvertResponse:
        """
        Convert a lead into Account + Contact + Deal in a single transaction.
        """
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException("Lead", lead_id)
        if lead.status == LeadStatus.CONVERTED:
            raise BadRequestException("Lead has already been converted")
        if lead.status != LeadStatus.QUALIFIED:
            raise BadRequestException(f"Only qualified leads can be converted. Current status: '{lead.status.value}'")

        # 1) Create Account — carry over all available lead data
        account = Account(
            name=payload.account_name or lead.company_name or lead.contact_name,
            email=lead.email,
            phone=lead.phone,
            notes=lead.notes,
            owner_user_id=lead.owner_user_id,
        )
        self.db.add(account)
        self.db.flush()  # get account.id

        # 2) Create Contact
        names = (payload.contact_first_name, payload.contact_last_name)
        if not names[0]:
            parts = lead.contact_name.split(" ", 1)
            names = (parts[0], parts[1] if len(parts) > 1 else "")

        contact = Contact(
            account_id=account.id,
            first_name=names[0],
            last_name=names[1] or "",
            email=lead.email,
            phone=lead.phone,
            notes=lead.notes,
        )
        self.db.add(contact)
        self.db.flush()

        # 3) Create Deal
        try:
            stage = DealStage(payload.deal_stage)
        except ValueError:
            stage = DealStage.QUALIFICATION

        deal = Deal(
            account_id=account.id,
            name=payload.deal_name or f"Deal - {account.name}",
            stage=stage,
            value=payload.deal_value or lead.estimated_value or 0,
            owner_user_id=lead.owner_user_id,
            notes=lead.notes,
        )
        self.db.add(deal)
        self.db.flush()

        # 4) Mark lead as converted and persist all references
        lead.status = LeadStatus.CONVERTED
        lead.converted_account_id = account.id
        lead.converted_contact_id = contact.id
        lead.converted_deal_id = deal.id

        self.db.commit()

        return LeadConvertResponse(
            lead_id=lead.id,
            account_id=account.id,
            contact_id=contact.id,
            deal_id=deal.id,
        )
