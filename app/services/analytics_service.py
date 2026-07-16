from typing import Dict, Any, List
from app.services.metrics_service import get_metrics_service, MetricsService
from app.services.trend_analysis import get_trend_analysis_service, TrendAnalysisService
from app.services.health_monitor import get_health_monitor_service, HealthMonitorService

class AnalyticsService:
    def __init__(
        self,
        metrics_service: MetricsService = None,
        trend_service: TrendAnalysisService = None,
        health_service: HealthMonitorService = None
    ):
        self.metrics_service = metrics_service or get_metrics_service()
        self.trend_service = trend_service or get_trend_analysis_service()
        self.health_service = health_service or get_health_monitor_service()

    def get_enterprise_analytics(self) -> Dict[str, Any]:
        metrics = self.metrics_service.get_comprehensive_metrics()
        sentiment_trends = self.trend_service.get_sentiment_trends(days=7)
        intent_trends = self.trend_service.get_intent_trends(days=7)
        rag_trends = self.trend_service.get_rag_success_trends(days=7)
        
        return {
            "overall_metrics": metrics,
            "trends": {
                "sentiment": sentiment_trends,
                "intent": intent_trends,
                "rag": rag_trends
            },
            "status": "COMPLETED"
        }

_global_analytics_service = AnalyticsService()

def get_analytics_service() -> AnalyticsService:
    return _global_analytics_service
