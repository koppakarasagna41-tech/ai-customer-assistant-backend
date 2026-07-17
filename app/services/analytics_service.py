from typing import Any

from app.services.health_monitor import HealthMonitorService, get_health_monitor_service
from app.services.metrics_service import MetricsService, get_metrics_service
from app.services.trend_analysis import TrendAnalysisService, get_trend_analysis_service


class AnalyticsService:
    def __init__(
        self,
        metrics_service: MetricsService = None,
        trend_service: TrendAnalysisService = None,
        health_service: HealthMonitorService = None,
    ):
        self.metrics_service = metrics_service or get_metrics_service()
        self.trend_service = trend_service or get_trend_analysis_service()
        self.health_service = health_service or get_health_monitor_service()

    def get_enterprise_analytics(self) -> dict[str, Any]:
        metrics = self.metrics_service.get_comprehensive_metrics()
        sentiment_trends = self.trend_service.get_sentiment_trends(days=7)
        intent_trends = self.trend_service.get_intent_trends(days=7)
        rag_trends = self.trend_service.get_rag_success_trends(days=7)

        return {
            "overall_metrics": metrics,
            "trends": {"sentiment": sentiment_trends, "intent": intent_trends, "rag": rag_trends},
            "status": "COMPLETED",
        }


_global_analytics_service = AnalyticsService()


def get_analytics_service() -> AnalyticsService:
    return _global_analytics_service
