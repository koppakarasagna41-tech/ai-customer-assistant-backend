from fastapi import APIRouter, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.schemas.response import BaseResponse
from app.schemas.dashboard import DashboardOverview
from app.schemas.analytics import DateRange, AnalyticsFilter
from app.schemas.chart import ChartData
from app.services.dashboard_service import get_dashboard_service, DashboardService
from app.services.analytics_service import get_analytics_service, AnalyticsService
from app.services.health_monitor import get_health_monitor_service, HealthMonitorService

router = APIRouter()

@router.get(
    "/dashboard",
    response_model=BaseResponse[DashboardOverview],
    status_code=status.HTTP_200_OK,
    summary="Get complete enterprise dashboard overview",
    description="Fetch key performance indicators, token usage, cost metrics, agent performance, and chart metadata for real-time visualization."
)
async def get_dashboard_overview(
    category: Optional[str] = Query(None, description="Filter metrics by ticket category"),
    priority: Optional[str] = Query(None, description="Filter metrics by priority level"),
    agent_id: Optional[str] = Query(None, description="Filter metrics by agent ID"),
    days: int = Query(7, description="Number of historical days for trends and charts (defaults to 7)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    date_range = DateRange(start_date=start_date, end_date=end_date)
    filters = AnalyticsFilter(category=category, priority=priority, agent_id=agent_id)
    
    dashboard = dashboard_service.get_dashboard(date_range, filters)
    return BaseResponse(
        success=True,
        message="Enterprise dashboard overview loaded successfully.",
        data=dashboard
    )

@router.get(
    "/analytics/raw",
    response_model=BaseResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get raw enterprise metrics and trends",
    description="Fetch unfiltered metrics, timeseries trend data, and RAG usage analysis."
)
async def get_raw_analytics(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    analytics = analytics_service.get_enterprise_analytics()
    return BaseResponse(
        success=True,
        message="Raw enterprise analytics retrieved successfully.",
        data=analytics
    )

@router.post(
    "/latency/record",
    status_code=status.HTTP_200_OK,
    summary="Record latency / request status",
    description="Developer diagnostic endpoint to feed latency data into the real-time health monitor."
)
async def record_latency(
    latency_ms: float = Query(..., description="API request latency in milliseconds"),
    is_error: bool = Query(False, description="Whether the request was an error"),
    health_service: HealthMonitorService = Depends(get_health_monitor_service)
):
    health_service.record_request(latency_ms, is_error)
    return BaseResponse(
        success=True,
        message="Request metrics registered with the health monitor.",
        data=None
    )
