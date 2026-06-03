"""
Audit domain — Model (journal d'audit).
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseEntity


class AuditLog(BaseEntity):
    __tablename__ = "audit_logs"

    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    entity = Column(String(100), nullable=False, index=True)   # e.g. "lead", "deal", "ticket"
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)                 # e.g. "create", "update", "delete", "stage_change"
    before_json = Column(Text, nullable=True)                   # JSON snapshot before
    after_json = Column(Text, nullable=True)                    # JSON snapshot after
    description = Column(String(500), nullable=True)            # human-readable summary

    # Relationships
    actor = relationship("User", lazy="joined")
