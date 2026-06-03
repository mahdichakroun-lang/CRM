"""
Quotes domain — Service.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.quotes.repository import QuoteRepository
from app.domain.quotes.schemas import (
    QuoteCreateRequest, QuoteUpdateRequest, QuoteResponse,
)
from app.shared.exceptions import NotFoundException


class QuoteService:
    def __init__(self, db: Session):
        self.repo = QuoteRepository(db)

    def create(self, payload: QuoteCreateRequest) -> QuoteResponse:
        from app.domain.deals.models import Deal, DealStage
        from app.shared.exceptions import BadRequestException
        
        deal = self.repo.db.query(Deal).filter(Deal.id == payload.deal_id).first()
        if not deal:
            raise NotFoundException("Deal", payload.deal_id)
            
        if deal.stage in [DealStage.WON, DealStage.LOST]:
            raise BadRequestException(f"Cannot create quotes for a closed deal ({deal.stage.value})")

        data = payload.model_dump(exclude_unset=True)
        quote = self.repo.create(data)
        return QuoteResponse.model_validate(quote)

    def get(self, quote_id: int) -> QuoteResponse:
        quote = self.repo.get_by_id(quote_id)
        if not quote:
            raise NotFoundException("Quote", quote_id)
        return QuoteResponse.model_validate(quote)

    def list(
        self, skip: int = 0, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[QuoteResponse], int]:
        quotes = self.repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.repo.count(filters=filters)
        return [QuoteResponse.model_validate(q) for q in quotes], total

    def get_by_deal(self, deal_id: int) -> List[QuoteResponse]:
        quotes = self.repo.get_by_deal(deal_id)
        return [QuoteResponse.model_validate(q) for q in quotes]

    def update(self, quote_id: int, payload: QuoteUpdateRequest) -> QuoteResponse:
        data = payload.model_dump(exclude_unset=True)
        quote = self.repo.update(quote_id, data)
        if not quote:
            raise NotFoundException("Quote", quote_id)
        return QuoteResponse.model_validate(quote)

    def delete(self, quote_id: int) -> None:
        if not self.repo.delete(quote_id):
            raise NotFoundException("Quote", quote_id)
