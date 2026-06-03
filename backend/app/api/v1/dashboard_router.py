"""
API Router — Dashboard (reports).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, require_roles
from app.domain.auth.models import User, UserRole
from app.domain.dashboard.service import DashboardService
from app.domain.dashboard.schemas import SalesReport, SupportReport, ActivityTimeline
from app.domain.audit.service import AuditService
from app.domain.audit.schemas import AuditLogResponse
from app.shared.pagination import PaginatedResponse
from typing import List

router = APIRouter(prefix="/reports", tags=["Dashboard / Reports"])


@router.get("/sales", response_model=SalesReport)
def sales_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.COMMERCIAL)
    ),
):
    """Sales KPIs: leads by source/status, pipeline summary, conversion rate, won value."""
    return DashboardService(db).sales_report()


@router.get("/support", response_model=SupportReport)
def support_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPPORT)
    ),
):
    """Support KPIs: open tickets, overdue, avg resolution time."""
    return DashboardService(db).support_report()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    page: int = 1,
    size: int = 50,
    entity: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    """View audit trail (admin/manager only)."""
    filters = {}
    if entity:
        filters["entity"] = entity
    if search:
        filters["description"] = search
    skip = (page - 1) * size
    service = AuditService(db)
    logs, total = service.list(skip=skip, limit=size, filters=filters)
    return logs


@router.get("/activity-timeline", response_model=ActivityTimeline)
def activity_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.COMMERCIAL, UserRole.SUPPORT)
    ),
):
    """Monthly activity timeline for the last 6 months (leads, deals, tickets)."""
    return DashboardService(db).activity_timeline()
