from pydantic import BaseModel, Field

from app.schemas.analytics import AnalyticsFilter, DateRange, GeneralAnalytics
from app.schemas.chart import ChartData
from app.schemas.kpi import KPIOverview


class DashboardOverview(BaseModel):
    date_range: DateRange = Field(
        ..., description="The time range of data in the dashboard"
    )

    filters: AnalyticsFilter = Field(
        ..., description="Applied search and analytics filters"
    )

    kpis: KPIOverview = Field(
        ..., description="Key Performance Indicators overview"
    )

    metrics: GeneralAnalytics = Field(
        ..., description="General metrics block"
    )

    # ✅ ADD THIS FIELD
    token_usage: dict = Field(
        default_factory=dict,
        description="LLM token usage statistics",
    )

    charts: list[ChartData] = Field(
        ..., description="Charts metadata and timeseries data for visual presentation"
    )

    last_updated: str = Field(
        ..., description="Timestamp of when this dashboard was computed"
    )