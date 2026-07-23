from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query

from app.schemas.analytics import AnalyticsFilter, DateRange
from app.schemas.dashboard import DashboardOverview
from app.schemas.response import BaseResponse
from app.services.dashboard_service import (
    DashboardService,
    get_dashboard_service,
)

router = APIRouter()


@router.get(
    "/",
    response_model=BaseResponse[DashboardOverview],
)
async def get_dashboard(
    days: int = Query(7, ge=1, le=90, description="Number of days to include"),
    category: str | None = Query(None, description="Optional category filter"),
    priority: str | None = Query(None, description="Optional priority filter"),
    agent_id: str | None = Query(None, description="Optional agent filter"),
    service: DashboardService = Depends(get_dashboard_service),
):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    date_range = DateRange(start_date=start_date, end_date=end_date)
    filters = AnalyticsFilter(category=category, priority=priority, agent_id=agent_id)
    dashboard = service.get_dashboard(date_range, filters)
    return BaseResponse(success=True, message="Dashboard retrieved successfully", data=dashboard)


@router.post(
    "/",
    response_model=BaseResponse[DashboardOverview],
)
async def get_dashboard_post(
    date_range: DateRange,
    filters: AnalyticsFilter,
    service: DashboardService = Depends(get_dashboard_service),
):
    dashboard = service.get_dashboard(date_range, filters)
    return BaseResponse(success=True, message="Dashboard retrieved successfully", data=dashboard)
