"""
Audit domain — Service.
Provides a simple way to log any action across all domains.
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.audit.repository import AuditLogRepository
from app.domain.audit.schemas import AuditLogResponse


class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditLogRepository(db)

    def log(
        self,
        actor_user_id: int,
        entity: str,
        entity_id: int,
        action: str,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Create an audit log entry."""
        self.repo.create({
            "actor_user_id": actor_user_id,
            "entity": entity,
            "entity_id": entity_id,
            "action": action,
            "before_json": json.dumps(before, default=str) if before else None,
            "after_json": json.dumps(after, default=str) if after else None,
            "description": description,
        })

    def get_entity_history(self, entity: str, entity_id: int) -> List[AuditLogResponse]:
        logs = self.repo.get_by_entity(entity, entity_id)
        return [AuditLogResponse.model_validate(l) for l in logs]

    def get_user_activity(self, user_id: int, skip: int = 0, limit: int = 50) -> List[AuditLogResponse]:
        logs = self.repo.get_by_actor(user_id, skip=skip, limit=limit)
        return [AuditLogResponse.model_validate(l) for l in logs]

    def list(
        self, skip: int = 0, limit: int = 50, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AuditLogResponse], int]:
        logs = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [AuditLogResponse.model_validate(l) for l in logs], total
