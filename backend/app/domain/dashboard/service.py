"""
Dashboard domain — Service (aggregates data from other domains).
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.domain.leads.repository import LeadRepository
from app.domain.leads.models import Lead, LeadStatus
from app.domain.deals.repository import DealRepository
from app.domain.deals.models import Deal, DealStage
from app.domain.tickets.repository import TicketRepository
from app.domain.tickets.models import Ticket, TicketStatus
from app.domain.dashboard.schemas import (
    SalesReport, SupportReport, PipelineStageSummary, ActivityTimeline, ActivityTimelinePoint,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.deal_repo = DealRepository(db)
        self.ticket_repo = TicketRepository(db)

    def _month_boundaries(self):
        """Return (start_this_month, start_prev_month, end_prev_month)."""
        now = datetime.now(timezone.utc)
        start_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_prev = start_this - timedelta(seconds=1)
        start_prev = end_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start_this, start_prev, end_prev

    def _pct_change(self, current, previous):
        """Calculate percentage change."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    def sales_report(self) -> SalesReport:
        # Leads
        total_leads = self.lead_repo.count()
        leads_by_source = {
            (source.value if hasattr(source, 'value') else str(source)): count
            for source, count in self.lead_repo.count_by_source()
        }
        leads_by_status = {
            (status.value if hasattr(status, 'value') else str(status)): count
            for status, count in self.lead_repo.count_by_status()
        }

        # Deals
        total_deals = self.deal_repo.count()
        pipeline_raw = self.deal_repo.pipeline_summary()
        pipeline_summary = [
            PipelineStageSummary(stage=(stage.value if hasattr(stage, 'value') else str(stage)), count=count, total_value=Decimal(str(value)))
            for stage, count, value in pipeline_raw
        ]
        total_won_value = self.deal_repo.total_won_value()

        # Lost count
        lost_count_val = next(
            (p.count for p in pipeline_summary if p.stage == DealStage.LOST.value), 0
        )

        # Conversion rate
        converted_count = leads_by_status.get(LeadStatus.CONVERTED.value, 0)
        conversion_rate = (converted_count / total_leads * 100) if total_leads > 0 else 0.0

        # ── Trend calculations ──
        start_this, start_prev, end_prev = self._month_boundaries()

        # Pipeline trend: active pipeline value this month vs last month
        active_pipeline_now = sum(
            p.total_value for p in pipeline_summary 
            if p.stage not in [DealStage.WON.value, DealStage.LOST.value]
        )
        prev_pipeline = (
            self.db.query(func.coalesce(func.sum(Deal.value), 0))
            .filter(Deal.stage.notin_([DealStage.WON, DealStage.LOST]))
            .filter(Deal.created_at < start_this)
            .scalar()
        ) or 0
        pipeline_trend = self._pct_change(active_pipeline_now, float(Decimal(str(prev_pipeline)))) if prev_pipeline else None

        # Conversion trend
        conv_this = self.db.query(Lead).filter(
            Lead.status == LeadStatus.CONVERTED, Lead.updated_at >= start_this
        ).count()
        conv_prev = self.db.query(Lead).filter(
            Lead.status == LeadStatus.CONVERTED, 
            Lead.updated_at >= start_prev, Lead.updated_at < start_this
        ).count()
        conversion_trend = self._pct_change(conv_this, conv_prev) if (conv_this + conv_prev) > 0 else None

        return SalesReport(
            total_leads=total_leads,
            leads_by_source=leads_by_source,
            leads_by_status=leads_by_status,
            total_deals=total_deals,
            pipeline_summary=pipeline_summary,
            total_won_value=total_won_value,
            total_lost_count=lost_count_val,
            conversion_rate=round(conversion_rate, 1),
            pipeline_trend=pipeline_trend,
            conversion_trend=conversion_trend,
        )

    def support_report(self) -> SupportReport:
        total_tickets = self.ticket_repo.count()
        open_tickets = self.ticket_repo.count_open()
        overdue_tickets = self.ticket_repo.count_overdue()
        avg_resolution = self.ticket_repo.avg_resolution_hours()

        tickets_by_status = {
            (status.value if hasattr(status, 'value') else str(status)): count
            for status, count in self.ticket_repo.count_by_status()
        }
        tickets_by_priority = {
            (priority.value if hasattr(priority, 'value') else str(priority)): count
            for priority, count in self.ticket_repo.count_by_priority()
        }

        # ── Trend calculations ──
        start_this, start_prev, end_prev = self._month_boundaries()

        open_this = self.db.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
            Ticket.created_at >= start_this
        ).count()
        open_prev = self.db.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
            Ticket.created_at >= start_prev, Ticket.created_at < start_this
        ).count()
        open_tickets_trend = self._pct_change(open_this, open_prev) if (open_this + open_prev) > 0 else None

        return SupportReport(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            overdue_tickets=overdue_tickets,
            avg_resolution_hours=avg_resolution,
            tickets_by_status=tickets_by_status,
            tickets_by_priority=tickets_by_priority,
            open_tickets_trend=open_tickets_trend,
            resolution_trend=None,  # Requires historical data to compare
        )

    def activity_timeline(self) -> ActivityTimeline:
        """Return monthly activity for the last 6 months."""
        now = datetime.now(timezone.utc)
        months = []
        month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                       "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

        for i in range(5, -1, -1):
            # Calculate start/end of each month
            dt = now - timedelta(days=i * 30)
            m_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if m_start.month == 12:
                m_end = m_start.replace(year=m_start.year + 1, month=1)
            else:
                m_end = m_start.replace(month=m_start.month + 1)

            label = month_names[m_start.month - 1]

            leads_count = self.db.query(func.count(Lead.id)).filter(
                Lead.created_at >= m_start, Lead.created_at < m_end
            ).scalar() or 0

            deals_count = self.db.query(func.count(Deal.id)).filter(
                Deal.created_at >= m_start, Deal.created_at < m_end
            ).scalar() or 0

            won_val = self.db.query(func.coalesce(func.sum(Deal.value), 0)).filter(
                Deal.stage == DealStage.WON,
                Deal.created_at >= m_start, Deal.created_at < m_end
            ).scalar() or 0

            tickets_count = self.db.query(func.count(Ticket.id)).filter(
                Ticket.created_at >= m_start, Ticket.created_at < m_end
            ).scalar() or 0

            months.append(ActivityTimelinePoint(
                month=label,
                leads=leads_count,
                deals=deals_count,
                won_value=float(won_val),
                tickets=tickets_count,
            ))

        return ActivityTimeline(timeline=months)
