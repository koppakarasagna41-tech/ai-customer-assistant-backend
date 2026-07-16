import random
from typing import Dict, Any, List
from app.services.token_usage_service import get_token_usage_service, TokenUsageService
from app.services.cost_analytics import get_cost_analytics_service, CostAnalyticsService
from app.services.health_monitor import get_health_monitor_service, HealthMonitorService

class MetricsService:
    def __init__(
        self,
        token_service: TokenUsageService = None,
        cost_service: CostAnalyticsService = None,
        health_service: HealthMonitorService = None
    ):
        self.token_service = token_service or get_token_usage_service()
        self.cost_service = cost_service or get_cost_analytics_service()
        self.health_service = health_service or get_health_monitor_service()

    def get_ticket_metrics(self) -> Dict[str, Any]:
        return {
            "total_tickets": 1240,
            "resolved_tickets": 1100,
            "pending_tickets": 105,
            "escalated_tickets": 35,
            "avg_resolution_time_hrs": 2.4,
            "avg_response_time_min": 12.5,
            "customer_satisfaction_score": 4.65, # out of 5
            "ai_confidence_score": 0.88
        }

    def get_intent_distribution(self) -> Dict[str, int]:
        return {
            "refund_request": 142,
            "technical_issue": 385,
            "billing_query": 210,
            "account_access": 98,
            "general_inquiry": 405
        }

    def get_sentiment_distribution(self) -> Dict[str, int]:
        return {
            "positive": 580,
            "neutral": 420,
            "negative": 240
        }

    def get_rag_metrics(self) -> Dict[str, Any]:
        return {
            "success_rate": 92.4,
            "total_queries": 4500,
            "hits": 4158,
            "misses": 342,
            "avg_relevance_score": 0.89
        }

    def get_agent_performance_metrics(self) -> List[Dict[str, Any]]:
        return [
            {
                "agent_id": "AG_001",
                "agent_name": "Alice Johnson",
                "assigned_tickets": 340,
                "resolved_tickets": 320,
                "avg_response_time_min": 10.2,
                "csat_score": 4.8
            },
            {
                "agent_id": "AG_002",
                "agent_name": "Bob Smith",
                "assigned_tickets": 410,
                "resolved_tickets": 380,
                "avg_response_time_min": 14.5,
                "csat_score": 4.5
            },
            {
                "agent_id": "AG_003",
                "agent_name": "Charlie Davis",
                "assigned_tickets": 490,
                "resolved_tickets": 400,
                "avg_response_time_min": 13.1,
                "csat_score": 4.6
            }
        ]

    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        tokens = self.token_service.get_aggregated_usage(days=7)
        costs = self.cost_service.get_cost_summary(days=7)
        health = self.health_service.get_health_metrics()
        
        ticket_metrics = self.get_ticket_metrics()
        
        return {
            "total_tickets": ticket_metrics["total_tickets"],
            "resolved_tickets": ticket_metrics["resolved_tickets"],
            "pending_tickets": ticket_metrics["pending_tickets"],
            "escalated_tickets": ticket_metrics["escalated_tickets"],
            "avg_resolution_time_hrs": ticket_metrics["avg_resolution_time_hrs"],
            "avg_response_time_min": ticket_metrics["avg_response_time_min"],
            "customer_satisfaction_score": ticket_metrics["customer_satisfaction_score"],
            "ai_confidence_score": ticket_metrics["ai_confidence_score"],
            "intent_distribution": self.get_intent_distribution(),
            "sentiment_distribution": self.get_sentiment_distribution(),
            "token_usage": tokens,
            "cost": costs,
            "rag": self.get_rag_metrics(),
            "agent_performance": self.get_agent_performance_metrics(),
            "system_health": {
                "api_uptime": health["api_uptime"],
                "p95_latency_ms": health["p95_latency_ms"],
                "error_rate": health["error_rate"]
            }
        }

_global_metrics_service = MetricsService()

def get_metrics_service() -> MetricsService:
    return _global_metrics_service
