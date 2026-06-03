"""
Activities domain — Service.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.activities.repository import ActivityRepository
from app.domain.activities.schemas import (
    ActivityCreateRequest, ActivityUpdateRequest, ActivityResponse,
)
from app.shared.exceptions import NotFoundException


class ActivityService:
    def __init__(self, db: Session):
        self.repo = ActivityRepository(db)

    def create(self, payload: ActivityCreateRequest, created_by: int) -> ActivityResponse:
        from app.shared.exceptions import BadRequestException
        
        data = payload.model_dump(exclude_unset=True)
        # 5. Require at least one linked entity for activities
        if not data.get("account_id") and not data.get("contact_id") and not data.get("deal_id"):
            raise BadRequestException("Activity must be linked to at least one entity (Account, Contact, or Deal)")
            
        data["created_by"] = created_by
        activity = self.repo.create(data)
        return ActivityResponse.model_validate(activity)

    def get(self, activity_id: int) -> ActivityResponse:
        activity = self.repo.get_by_id(activity_id)
        if not activity:
            raise NotFoundException("Activity", activity_id)
        return ActivityResponse.model_validate(activity)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[ActivityResponse], int]:
        activities = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [ActivityResponse.model_validate(a) for a in activities], total

    def get_by_account(self, account_id: int) -> List[ActivityResponse]:
        activities = self.repo.get_by_account(account_id)
        return [ActivityResponse.model_validate(a) for a in activities]

    def get_by_deal(self, deal_id: int) -> List[ActivityResponse]:
        activities = self.repo.get_by_deal(deal_id)
        return [ActivityResponse.model_validate(a) for a in activities]

    def update(self, activity_id: int, payload: ActivityUpdateRequest) -> ActivityResponse:
        data = payload.model_dump(exclude_unset=True)
        activity = self.repo.update(activity_id, data)
        if not activity:
            raise NotFoundException("Activity", activity_id)
        return ActivityResponse.model_validate(activity)

    def delete(self, activity_id: int) -> None:
        if not self.repo.delete(activity_id):
            raise NotFoundException("Activity", activity_id)
