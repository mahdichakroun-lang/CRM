"""
Email Helpers — Resolve client email and name from CRM entities.

These helpers query the database to find the appropriate email recipient
for notifications related to tickets, quotes, etc.
"""
import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.auth.models import User, UserRole
from app.domain.accounts.models import Account
from app.domain.contacts.models import Contact
from app.domain.tickets.models import Ticket
from app.domain.deals.models import Deal

logger = logging.getLogger("crm.email")


def get_client_email_for_ticket(db: Session, ticket_id: int) -> Optional[Tuple[str, str]]:
    """
    Resolve the client email & name for a ticket notification.

    Priority:
    1. Client user linked to the ticket's account (User with role=client & account_id)
    2. Contact linked to the ticket (contact.email)
    3. Account email (account.email)

    Returns: (email, name) or None if no email found.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return None

    # 1. Try to find a client user linked to this account
    client_user = (
        db.query(User)
        .filter(
            User.role == UserRole.CLIENT,
            User.account_id == ticket.account_id,
            User.is_active == True,  # noqa: E712
        )
        .first()
    )
    if client_user and client_user.email:
        return (client_user.email, client_user.name)

    # 2. Try the contact linked to the ticket
    if ticket.contact_id:
        contact = db.query(Contact).filter(Contact.id == ticket.contact_id).first()
        if contact and contact.email:
            return (contact.email, f"{contact.first_name} {contact.last_name}")

    # 3. Fallback to account email
    account = db.query(Account).filter(Account.id == ticket.account_id).first()
    if account and account.email:
        return (account.email, account.name)

    logger.warning(f"📧 Aucun email trouvé pour le ticket #{ticket_id} — notification ignorée")
    return None


def get_client_email_for_quote(db: Session, deal_id: int) -> Optional[Tuple[str, str]]:
    """
    Resolve the client email & name for a quote notification.

    Priority:
    1. Client user linked to the deal's account
    2. Account email

    Returns: (email, name) or None if no email found.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return None

    # 1. Try to find a client user linked to this account
    client_user = (
        db.query(User)
        .filter(
            User.role == UserRole.CLIENT,
            User.account_id == deal.account_id,
            User.is_active == True,  # noqa: E712
        )
        .first()
    )
    if client_user and client_user.email:
        return (client_user.email, client_user.name)

    # 2. Fallback to account email
    account = db.query(Account).filter(Account.id == deal.account_id).first()
    if account and account.email:
        return (account.email, account.name)

    logger.warning(f"📧 Aucun email trouvé pour le deal #{deal_id} — notification ignorée")
    return None


def get_ticket_subject(db: Session, ticket_id: int) -> str:
    """Get the ticket subject for email notifications."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    return ticket.subject if ticket else f"Ticket #{ticket_id}"
