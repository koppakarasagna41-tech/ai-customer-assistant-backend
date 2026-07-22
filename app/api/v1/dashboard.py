from fastapi import APIRouter, Depends

from app.schemas.analytics import AnalyticsFilter, DateRange
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import (
    DashboardService,
    get_dashboard_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=DashboardOverview,
)
async def get_dashboard(
    date_range: DateRange,
    filters: AnalyticsFilter,
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_dashboard(date_range, filters)
