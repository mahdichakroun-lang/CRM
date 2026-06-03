"""
Audit domain — Repository.
"""
from typing import List
from sqlalchemy.orm import Session
from app.shared.base_repository import BaseRepository
from app.domain.audit.models import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def get_by_entity(self, entity: str, entity_id: int) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.entity == entity, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_by_actor(self, user_id: int, skip: int = 0, limit: int = 50) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.actor_user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip).limit(limit).all()
        )
