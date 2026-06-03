"""
Contacts domain — Model.
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class Contact(BaseEntity):
    __tablename__ = "contacts"

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    position = Column(String(150), nullable=True)  # e.g. CEO, CTO, DSI
    notes = Column(Text, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="contacts")
