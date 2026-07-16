from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.analytics import GeneralAnalytics, DateRange, AnalyticsFilter
from app.schemas.kpi import KPIOverview
from app.schemas.chart import ChartData

class DashboardOverview(BaseModel):
    date_range: DateRange = Field(..., description="The time range of data in the dashboard")
    filters: AnalyticsFilter = Field(..., description="Applied search and analytics filters")
    kpis: KPIOverview = Field(..., description="Key Performance Indicators overview")
    metrics: GeneralAnalytics = Field(..., description="General metrics block")
    charts: List[ChartData] = Field(..., description="Charts metadata and timeseries data for visual presentation")
    last_updated: str = Field(..., description="Timestamp of when this dashboard was computed")
