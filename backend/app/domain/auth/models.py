"""
Auth domain — User model (SQLAlchemy entity).
"""
import enum
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    MANAGER = "manager"
    CLIENT = "client"


class User(BaseEntity):
    __tablename__ = "users"

    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SAEnum(UserRole, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False, default=UserRole.COMMERCIAL
    )
    is_active = Column(Boolean, default=True, nullable=False)
    phone = Column(String(30), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    # FK: links a CLIENT-role user to the Account they belong to.
    # This is NOT the same as Account.owner_user_id (which tracks the internal
    # commercial user responsible for managing that account).
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    client_account = relationship("Account", foreign_keys=[account_id], lazy="joined")
