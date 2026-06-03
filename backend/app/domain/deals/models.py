"""
Deals domain — Model (pipeline opportunities).
"""
import enum
from sqlalchemy import Column, String, Integer, Numeric, Date, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class DealStage(str, enum.Enum):
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"       # Devis
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Deal(BaseEntity):
    __tablename__ = "deals"

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    stage = Column(SAEnum(DealStage), nullable=False, default=DealStage.QUALIFICATION, index=True)
    value = Column(Numeric(15, 2), nullable=True, default=0)  # Montant estimé
    probability = Column(Integer, nullable=True, default=0)  # % de chance
    expected_close_date = Column(Date, nullable=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    lost_reason = Column(String(500), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="deals")
    owner = relationship("User", foreign_keys=[owner_user_id], lazy="joined")
    quotes = relationship("Quote", back_populates="deal", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True)
