"""
Quotes domain — Model (devis).
"""
import enum
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Quote(BaseEntity):
    __tablename__ = "quotes"

    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    reference = Column(String(50), nullable=True, unique=True)  # e.g. DEV-2026-001
    amount = Column(Numeric(15, 2), nullable=False, default=0)
    status = Column(SAEnum(QuoteStatus), nullable=False, default=QuoteStatus.DRAFT)
    pdf_url = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)

    # Relationships
    deal = relationship("Deal", back_populates="quotes")
