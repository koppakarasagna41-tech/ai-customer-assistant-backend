from datetime import datetime
from typing import List
from app.schemas.dashboard import DashboardOverview
from app.schemas.analytics import DateRange, AnalyticsFilter, GeneralAnalytics
from app.schemas.chart import ChartData, ChartDataItem
from app.services.kpi_service import get_kpi_service, KPIService
from app.services.metrics_service import get_metrics_service, MetricsService
from app.services.trend_analysis import get_trend_analysis_service, TrendAnalysisService
from app.services.cache_service import get_cache_service, CacheService

class DashboardService:
    def __init__(
        self,
        kpi_service: KPIService = None,
        metrics_service: MetricsService = None,
        trend_service: TrendAnalysisService = None,
        cache_service: CacheService = None
    ):
        self.kpi_service = kpi_service or get_kpi_service()
        self.metrics_service = metrics_service or get_metrics_service()
        self.trend_service = trend_service or get_trend_analysis_service()
        self.cache_service = cache_service or get_cache_service()

    def get_dashboard(self, date_range: DateRange, filters: AnalyticsFilter) -> DashboardOverview:
        # Construct cache key based on dates and filters
        cache_key = f"dashboard_{date_range.start_date.isoformat()}_{date_range.end_date.isoformat()}_{filters.category}_{filters.priority}_{filters.agent_id}"
        
        cached_dashboard = self.cache_service.get(cache_key)
        if cached_dashboard:
            return cached_dashboard

        # Load metrics & KPIs
        kpis = self.kpi_service.get_kpi_overview()
        raw_metrics = self.metrics_service.get_comprehensive_metrics()
        
        # Apply filters in a real setup (we simulate it)
        metrics = GeneralAnalytics(**raw_metrics)

        # Build Charts
        charts = []
        
        # 1. Sentiment Trends Chart
        sent_trends = self.trend_service.get_sentiment_trends(days=7)
        charts.append(
            ChartData(
                chart_type="line",
                title="Sentiment Volume Trends (7 Days)",
                data=[
                    ChartDataItem(label=item["date"], value=float(item["positive"] + item["neutral"] - item["negative"]))
                    for item in sent_trends
                ],
                x_axis_label="Date",
                y_axis_label="Sentiment Index"
            )
        )

        # 2. Intent Distribution Chart
        charts.append(
            ChartData(
                chart_type="pie",
                title="Top Request Intents",
                data=[
                    ChartDataItem(label=k, value=float(v))
                    for k, v in metrics.intent_distribution.items()
                ],
                x_axis_label="Intent Category",
                y_axis_label="Volume"
            )
        )

        # 3. RAG Success Rate Timeseries
        rag_trends = self.trend_service.get_rag_success_trends(days=7)
        charts.append(
            ChartData(
                chart_type="area",
                title="AI RAG Success Rate Trends",
                data=[
                    ChartDataItem(label=item["date"], value=float(item["success_rate"]))
                    for item in rag_trends
                ],
                x_axis_label="Date",
                y_axis_label="Success Rate (%)"
            )
        )

        dashboard = DashboardOverview(
            date_range=date_range,
            filters=filters,
            kpis=kpis,
            metrics=metrics,
            charts=charts,
            last_updated=datetime.utcnow().isoformat() + "Z"
        )

        # Cache for 10 minutes to respect tokenomics
        self.cache_service.set(cache_key, dashboard, ttl_seconds=600)
        return dashboard

_global_dashboard_service = DashboardService()

def get_dashboard_service() -> DashboardService:
    return _global_dashboard_service
