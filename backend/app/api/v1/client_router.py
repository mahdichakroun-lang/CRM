"""
API Router — Client Portal (restricted access for client users).
Clients can view/create tickets, messages, and view their quotes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.domain.auth.models import User, UserRole
from app.domain.tickets.models import Ticket, TicketMessage, TicketPriority, TicketStatus, TicketCategory
from app.domain.quotes.models import Quote
from app.domain.deals.models import Deal
from app.domain.accounts.models import Account
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/client", tags=["Client Portal"])


# ── Guard: only client role ──
def get_client_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Access reserved for client users")
    if not current_user.account_id:
        raise HTTPException(status_code=403, detail="Client not linked to any account")
    return current_user


# ── Schemas ──
class ClientTicketCreate(BaseModel):
    subject: str
    description: Optional[str] = None
    category: TicketCategory = TicketCategory.SUPPORT
    priority: TicketPriority = TicketPriority.MEDIUM

class ClientMessageCreate(BaseModel):
    message: str

class ClientTicketResponse(BaseModel):
    id: int
    subject: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class ClientMessageResponse(BaseModel):
    id: int
    message: str
    is_internal: bool = False
    created_at: datetime
    author_name: Optional[str] = None
    model_config = {"from_attributes": True}

class ClientQuoteResponse(BaseModel):
    id: int
    reference: Optional[str] = None
    amount: Decimal
    status: Optional[str] = None
    deal_name: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}

class ClientAccountInfo(BaseModel):
    id: int
    name: str
    sector: Optional[str] = None
    city: Optional[str] = None
    model_config = {"from_attributes": True}

class ClientDashboard(BaseModel):
    account_name: str
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    total_quotes: int
    accepted_quotes: int
    total_quotes_value: Decimal


# ── Endpoints ──

@router.get("/dashboard", response_model=ClientDashboard)
def client_dashboard(client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """Client dashboard with summary stats."""
    account = db.query(Account).filter(Account.id == client.account_id).first()
    tickets = db.query(Ticket).filter(Ticket.account_id == client.account_id).all()
    deals = db.query(Deal).filter(Deal.account_id == client.account_id).all()
    deal_ids = [d.id for d in deals]
    quotes = db.query(Quote).filter(Quote.deal_id.in_(deal_ids)).all() if deal_ids else []

    return ClientDashboard(
        account_name=account.name if account else "N/A",
        total_tickets=len(tickets),
        open_tickets=len([t for t in tickets if t.status in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_CUSTOMER)]),
        resolved_tickets=len([t for t in tickets if t.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED)]),
        total_quotes=len(quotes),
        accepted_quotes=len([q for q in quotes if q.status and q.status.value == "accepted"]),
        total_quotes_value=sum((q.amount or Decimal("0") for q in quotes), Decimal("0")),
    )


@router.get("/tickets")
def client_list_tickets(client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """List tickets for the client's account (excludes internal notes)."""
    tickets = db.query(Ticket).filter(Ticket.account_id == client.account_id).order_by(Ticket.created_at.desc()).all()
    result = []
    for t in tickets:
        result.append({
            "id": t.id, "subject": t.subject, "description": t.description,
            "category": t.category.value if t.category else None,
            "priority": t.priority.value if t.priority else None,
            "status": t.status.value if t.status else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        })
    return result


@router.post("/tickets", status_code=201)
def client_create_ticket(payload: ClientTicketCreate, client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """Client creates a new support ticket."""
    ticket = Ticket(
        account_id=client.account_id,
        subject=payload.subject,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        status=TicketStatus.OPEN,
        created_by=client.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {
        "id": ticket.id, "subject": ticket.subject,
        "status": ticket.status.value if ticket.status else None,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }


@router.get("/tickets/{ticket_id}")
def client_get_ticket(ticket_id: int, client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """Get ticket detail (must belong to client account)."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.account_id == client.account_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "id": ticket.id, "subject": ticket.subject, "description": ticket.description,
        "category": ticket.category.value if ticket.category else None,
        "priority": ticket.priority.value if ticket.priority else None,
        "status": ticket.status.value if ticket.status else None,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
    }


@router.get("/tickets/{ticket_id}/messages")
def client_get_messages(ticket_id: int, client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """Get messages for a ticket, excluding internal notes."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.account_id == client.account_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # Only show public messages (not internal notes)
    msgs = db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id, TicketMessage.is_internal == False).order_by(TicketMessage.created_at.asc()).all()
    result = []
    for m in msgs:
        author = db.query(User).filter(User.id == m.author_user_id).first()
        result.append({
            "id": m.id, "message": m.message, "is_internal": m.is_internal,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "author_name": author.name if author else "Support",
        })
    return result


@router.post("/tickets/{ticket_id}/messages", status_code=201)
def client_send_message(ticket_id: int, payload: ClientMessageCreate, client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """Client sends a message on their ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.account_id == client.account_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    msg = TicketMessage(ticket_id=ticket_id, author_user_id=client.id, message=payload.message, is_internal=False)
    db.add(msg)
    # If ticket was waiting_customer, move to in_progress
    if ticket.status == TicketStatus.WAITING_CUSTOMER:
        ticket.status = TicketStatus.IN_PROGRESS
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "message": msg.message, "created_at": msg.created_at.isoformat() if msg.created_at else None}


@router.get("/quotes")
def client_list_quotes(client: User = Depends(get_client_user), db: Session = Depends(get_db)):
    """List quotes for the client's account (via deals)."""
    deals = db.query(Deal).filter(Deal.account_id == client.account_id).all()
    deal_ids = [d.id for d in deals]
    deal_map = {d.id: d.name for d in deals}
    if not deal_ids:
        return []
    quotes = db.query(Quote).filter(Quote.deal_id.in_(deal_ids)).order_by(Quote.created_at.desc()).all()
    result = []
    for q in quotes:
        result.append({
            "id": q.id, "reference": q.reference, "amount": q.amount,
            "status": q.status.value if q.status else None,
            "deal_name": deal_map.get(q.deal_id, "N/A"),
            "created_at": q.created_at.isoformat() if q.created_at else None,
        })
    return result
