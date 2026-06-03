"""
Activities domain — Model (timeline events).
"""
import enum
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"


class Activity(BaseEntity):
    __tablename__ = "activities"

    type = Column(SAEnum(ActivityType), nullable=False)
    subject = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)  # prochaine relance

    # Optional FK links to related business entities.
    # Each FK is independent and nullable — an Activity can reference one or more entities.
    # Note: this is NOT generic polymorphism (entity_type + entity_id pattern).
    # Validation "at least one linked entity" is enforced in ActivityService.create().
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    account = relationship("Account", lazy="joined")
    contact = relationship("Contact", lazy="joined")
    deal = relationship("Deal", lazy="joined")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
