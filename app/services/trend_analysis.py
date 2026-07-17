from datetime import datetime, timedelta
from typing import Any


class TrendAnalysisService:
    def get_sentiment_trends(self, days: int = 7) -> list[dict[str, Any]]:
        trends = []
        now = datetime.utcnow()
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            # Simulated changing trends
            trends.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "positive": 45 + (i % 3) * 5,
                    "neutral": 30 - (i % 2) * 3,
                    "negative": 25 - (i % 4) * 4,
                }
            )
        return trends

    def get_intent_trends(self, days: int = 7) -> list[dict[str, Any]]:
        trends = []
        now = datetime.utcnow()
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            trends.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "refund_request": 10 + (i % 3) * 2,
                    "technical_issue": 25 + (i % 5) * 3,
                    "billing_query": 15 + (i % 2) * 4,
                    "account_access": 8 + (i % 4) * 1,
                    "general_inquiry": 42 - (i % 3) * 3,
                }
            )
        return trends

    def get_rag_success_trends(self, days: int = 7) -> list[dict[str, Any]]:
        trends = []
        now = datetime.utcnow()
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            trends.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "success_rate": round(88.5 + (i % 3) * 1.5, 2),
                    "total_queries": 150 + (i % 2) * 20,
                }
            )
        return trends


_global_trend_analysis_service = TrendAnalysisService()


def get_trend_analysis_service() -> TrendAnalysisService:
    return _global_trend_analysis_service
