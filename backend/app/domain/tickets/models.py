"""
Tickets domain — Models (Helpdesk).
"""
import enum
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, enum.Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SUPPORT = "support"
    QUESTION = "question"
    INCIDENT = "incident"
    OTHER = "other"


class Ticket(BaseEntity):
    __tablename__ = "tickets"

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SAEnum(TicketCategory), nullable=False, default=TicketCategory.SUPPORT)
    priority = Column(SAEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM, index=True)
    status = Column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)  # SLA deadline
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="tickets")
    contact = relationship("Contact", lazy="joined")
    assignee = relationship("User", foreign_keys=[assigned_to], lazy="joined")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
    messages = relationship("TicketMessage", back_populates="ticket", lazy="dynamic",
                            order_by="TicketMessage.created_at")


class TicketMessage(BaseEntity):
    __tablename__ = "ticket_messages"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # True = internal note, False = public reply

    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    author = relationship("User", lazy="joined")
