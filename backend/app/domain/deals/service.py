"""
Deals domain — Service.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.deals.repository import DealRepository
from app.domain.deals.models import DealStage
from app.domain.deals.schemas import (
    DealCreateRequest, DealUpdateRequest, DealStageUpdateRequest, DealResponse,
)
from app.shared.exceptions import NotFoundException, BadRequestException


class DealService:
    def __init__(self, db: Session):
        self.repo = DealRepository(db)

    def create(self, payload: DealCreateRequest) -> DealResponse:
        data = payload.model_dump(exclude_unset=True)
        deal = self.repo.create(data)
        return DealResponse.model_validate(deal)

    def get(self, deal_id: int) -> DealResponse:
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundException("Deal", deal_id)
        return DealResponse.model_validate(deal)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[DealResponse], int]:
        deals = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [DealResponse.model_validate(d) for d in deals], total

    def update(self, deal_id: int, payload: DealUpdateRequest) -> DealResponse:
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundException("Deal", deal_id)

        data = payload.model_dump(exclude_unset=True)

        # Enforce same rules as `update_stage` if stage is being modified
        if "stage" in data:
            new_stage = data["stage"]
            # Allow changing stage from WON/LOST
            if new_stage == DealStage.LOST and not data.get("lost_reason"):
                raise BadRequestException("lost_reason is required when stage is 'lost'")
            
            probability_map = {
                DealStage.QUALIFICATION: 30,
                DealStage.PROPOSAL: 50,
                DealStage.NEGOTIATION: 80,
                DealStage.WON: 100,
                DealStage.LOST: 0,
            }
            if "probability" not in data:
                data["probability"] = probability_map.get(new_stage, deal.probability)
            
            if data.get("lost_reason") and new_stage != DealStage.LOST:
                 data["lost_reason"] = None

        updated_deal = self.repo.update(deal_id, data)
        return DealResponse.model_validate(updated_deal)

    def update_stage(self, deal_id: int, payload: DealStageUpdateRequest) -> DealResponse:
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            raise NotFoundException("Deal", deal_id)

        # 1. Validate Pipeline Transitions
        # Allowed to move out of closed states

        if payload.stage == DealStage.LOST and not payload.lost_reason:
            raise BadRequestException("lost_reason is required when stage is 'lost'")

        # 2. Auto-update probability based on new stage
        probability_map = {
            DealStage.QUALIFICATION: 30,
            DealStage.PROPOSAL: 50,
            DealStage.NEGOTIATION: 80,
            DealStage.WON: 100,
            DealStage.LOST: 0,
        }
        
        update_data: Dict[str, Any] = {
            "stage": payload.stage,
            "probability": probability_map.get(payload.stage, deal.probability)
        }
        
        if payload.lost_reason:
            update_data["lost_reason"] = payload.lost_reason
        elif payload.stage != DealStage.LOST:
            update_data["lost_reason"] = None # Clear if reopened or moved somehow

        deal = self.repo.update(deal_id, update_data)
        return DealResponse.model_validate(deal)

    def delete(self, deal_id: int) -> None:
        db = self.repo.db
        from app.domain.quotes.models import Quote
        from app.domain.activities.models import Activity
        # Cascade: delete child quotes (ON DELETE CASCADE in model)
        db.query(Quote).filter(Quote.deal_id == deal_id).delete(synchronize_session=False)
        # Clear activity references (ON DELETE SET NULL in model)
        db.query(Activity).filter(Activity.deal_id == deal_id).update(
            {"deal_id": None}, synchronize_session=False
        )
        db.flush()
        if not self.repo.delete(deal_id):
            raise NotFoundException("Deal", deal_id)

    def get_by_account(self, account_id: int) -> List[DealResponse]:
        deals = self.repo.get_by_account(account_id)
        return [DealResponse.model_validate(d) for d in deals]
