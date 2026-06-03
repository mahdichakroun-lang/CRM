"""
Accounts domain — Model (entreprises clientes).
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class Account(BaseEntity):
    __tablename__ = "accounts"

    name = Column(String(255), nullable=False, index=True)
    sector = Column(String(100), nullable=True)  # e.g. IT, Finance, Industry
    industry = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    # FK: internal commercial user responsible for this account.
    # This is NOT the same as User.account_id (which links a CLIENT-role user
    # to the account they belong to — the reverse direction).
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_user_id], lazy="joined")
    contacts = relationship("Contact", back_populates="account", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True)
    deals = relationship("Deal", back_populates="account", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True)
    tickets = relationship("Ticket", back_populates="account", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True)
