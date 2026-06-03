"""
Leads domain — Model (prospects).
"""
import enum
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    PHONE = "phone"
    REFERRAL = "referral"
    TRADE_SHOW = "trade_show"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    OTHER = "other"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"


class Lead(BaseEntity):
    __tablename__ = "leads"

    company_name = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    source = Column(SAEnum(LeadSource), nullable=False, default=LeadSource.OTHER)
    status = Column(SAEnum(LeadStatus), nullable=False, default=LeadStatus.NEW, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    estimated_value = Column(Integer, nullable=True)  # valeur estimée en DT

    # Set after conversion — references to the entities created by LeadService.convert()
    converted_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    converted_contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    converted_deal_id = Column(Integer, ForeignKey("deals.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_user_id], lazy="joined")
