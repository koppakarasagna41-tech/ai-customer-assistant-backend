from app.services.token_usage_service import get_token_usage_service, TokenUsageService
from typing import Dict, Any, List

class CostAnalyticsService:
    def __init__(self, token_usage_service: TokenUsageService = None):
        self.token_usage_service = token_usage_service or get_token_usage_service()
        # Pricing per 1000 tokens (e.g., standard Gemini/enterprise LLM pricing)
        self.prompt_token_cost_1k = 0.00015
        self.completion_token_cost_1k = 0.0006

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        prompt_cost = (prompt_tokens / 1000.0) * self.prompt_token_cost_1k
        completion_cost = (completion_tokens / 1000.0) * self.completion_token_cost_1k
        return round(prompt_cost + completion_cost, 4)

    def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        token_summary = self.token_usage_service.get_aggregated_usage(days=days)
        total_cost = self.calculate_cost(
            token_summary["prompt_tokens"],
            token_summary["completion_tokens"]
        )
        
        # Assume average of 10 tickets resolved per day on average in that period
        avg_tickets = 120
        cost_per_ticket = round(total_cost / max(1, avg_tickets), 4)

        return {
            "total_cost_usd": total_cost,
            "cost_per_ticket": cost_per_ticket,
            "currency": "USD",
            "pricing_model": {
                "prompt_cost_per_1k": self.prompt_token_cost_1k,
                "completion_cost_per_1k": self.completion_token_cost_1k
            }
        }

    def get_cost_trend(self) -> List[Dict[str, Any]]:
        history = self.token_usage_service.get_history()
        trend = []
        for entry in history:
            cost = self.calculate_cost(entry["prompt_tokens"], entry["completion_tokens"])
            trend.append({
                "timestamp": entry["timestamp"],
                "cost": cost,
                "total_tokens": entry["total_tokens"]
            })
        return trend

_global_cost_analytics_service = CostAnalyticsService()

def get_cost_analytics_service() -> CostAnalyticsService:
    return _global_cost_analytics_service
