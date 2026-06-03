"""
Accounts domain — Service (business logic).
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.accounts.repository import AccountRepository
from app.domain.accounts.schemas import (
    AccountCreateRequest, AccountUpdateRequest, AccountResponse,
)
from app.shared.exceptions import NotFoundException


class AccountService:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, payload: AccountCreateRequest) -> AccountResponse:
        data = payload.model_dump(exclude_unset=True)
        account = self.repo.create(data)
        return AccountResponse.model_validate(account)

    def get(self, account_id: int) -> AccountResponse:
        account = self.repo.get_by_id(account_id)
        if not account:
            raise NotFoundException("Account", account_id)
        return AccountResponse.model_validate(account)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AccountResponse], int]:
        accounts = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [AccountResponse.model_validate(a) for a in accounts], total

    def update(self, account_id: int, payload: AccountUpdateRequest) -> AccountResponse:
        data = payload.model_dump(exclude_unset=True)
        account = self.repo.update(account_id, data)
        if not account:
            raise NotFoundException("Account", account_id)
        return AccountResponse.model_validate(account)

    def delete(self, account_id: int) -> None:
        db = self.repo.db
        # Cascade delete in FK-safe order
        from app.domain.tickets.models import Ticket, TicketMessage
        from app.domain.deals.models import Deal
        from app.domain.quotes.models import Quote
        from app.domain.contacts.models import Contact
        from app.domain.activities.models import Activity

        # 1. Delete ticket messages for this account's tickets
        ticket_ids = [t.id for t in db.query(Ticket.id).filter(Ticket.account_id == account_id).all()]
        if ticket_ids:
            db.query(TicketMessage).filter(TicketMessage.ticket_id.in_(ticket_ids)).delete(synchronize_session=False)
        # 2. Delete tickets
        db.query(Ticket).filter(Ticket.account_id == account_id).delete(synchronize_session=False)
        # 3. Delete quotes for this account's deals
        deal_ids = [d.id for d in db.query(Deal.id).filter(Deal.account_id == account_id).all()]
        if deal_ids:
            db.query(Quote).filter(Quote.deal_id.in_(deal_ids)).delete(synchronize_session=False)
        # 4. Delete deals
        db.query(Deal).filter(Deal.account_id == account_id).delete(synchronize_session=False)
        # 5. Delete activities
        db.query(Activity).filter(Activity.account_id == account_id).delete(synchronize_session=False)
        # 6. Delete contacts
        db.query(Contact).filter(Contact.account_id == account_id).delete(synchronize_session=False)
        db.flush()
        # 7. Delete account
        if not self.repo.delete(account_id):
            raise NotFoundException("Account", account_id)

