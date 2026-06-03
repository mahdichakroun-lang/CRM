"""
Dashboard domain — Schemas (response DTOs for reports).
"""
from typing import Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel


class PipelineStageSummary(BaseModel):
    stage: str
    count: int
    total_value: float


class SalesReport(BaseModel):
    total_leads: int
    leads_by_source: Dict[str, int]
    leads_by_status: Dict[str, int]
    total_deals: int
    pipeline_summary: List[PipelineStageSummary]
    total_won_value: float
    total_lost_count: int
    conversion_rate: float  # leads converted / total leads * 100
    # Trends (N vs N-1 month, percentage)
    pipeline_trend: Optional[float] = None
    conversion_trend: Optional[float] = None


class SupportReport(BaseModel):
    total_tickets: int
    open_tickets: int
    overdue_tickets: int
    avg_resolution_hours: float
    tickets_by_status: Dict[str, int]
    tickets_by_priority: Dict[str, int]
    # Trends
    open_tickets_trend: Optional[float] = None
    resolution_trend: Optional[float] = None


class ActivityTimelinePoint(BaseModel):
    month: str  # e.g. "Jan", "Fév", "Mar"
    leads: int = 0
    deals: int = 0
    won_value: float = 0.0
    tickets: int = 0


class ActivityTimeline(BaseModel):
    timeline: List[ActivityTimelinePoint]
