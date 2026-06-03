"""
Audit domain — Schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: int
    entity: str
    entity_id: int
    action: str
    before_json: Optional[str] = None
    after_json: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
