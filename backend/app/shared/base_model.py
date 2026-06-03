"""
Shared base model for all SQLAlchemy domain entities.
Provides common columns: id, created_at, updated_at.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.database import Base


class BaseEntity(Base):
    """Abstract base class for all domain entities."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
