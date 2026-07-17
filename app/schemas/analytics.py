from datetime import datetime

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start_date: datetime = Field(..., description="Start date of the analytics window")
    end_date: datetime = Field(..., description="End date of the analytics window")


class AnalyticsFilter(BaseModel):
    category: str | None = Field(None, description="Optional filter by ticket category")
    priority: str | None = Field(None, description="Optional filter by priority")
    agent_id: str | None = Field(None, description="Optional filter by agent ID")


class TokenUsageMetrics(BaseModel):
    prompt_tokens: int = Field(..., description="Total input/prompt tokens used")
    completion_tokens: int = Field(..., description="Total output/completion tokens used")
    total_tokens: int = Field(..., description="Sum of prompt and completion tokens")


class CostMetrics(BaseModel):
    total_cost_usd: float = Field(..., description="Estimated cost in USD")
    cost_per_ticket: float = Field(..., description="Average AI cost per support ticket")


class RAGMetrics(BaseModel):
    success_rate: float = Field(..., description="Retrieval success rate (successful matches)")
    total_queries: int = Field(..., description="Total RAG queries made")
    hits: int = Field(..., description="Knowledge base hits")
    misses: int = Field(..., description="Knowledge base misses")
    avg_relevance_score: float = Field(
        ..., description="Average semantic similarity relevance score"
    )


class AgentPerformanceDetail(BaseModel):
    agent_id: str = Field(..., description="ID of the agent")
    agent_name: str = Field(..., description="Name of the support agent")
    assigned_tickets: int = Field(..., description="Number of tickets assigned")
    resolved_tickets: int = Field(..., description="Number of tickets resolved")
    avg_response_time_min: float = Field(..., description="Average response time in minutes")
    csat_score: float = Field(..., description="Customer satisfaction score for this agent")


class SystemHealthMetrics(BaseModel):
    api_uptime: float = Field(..., description="API Uptime percentage")
    p95_latency_ms: float = Field(..., description="P95 API request latency in milliseconds")
    error_rate: float = Field(..., description="API error rate percentage")


class GeneralAnalytics(BaseModel):
    total_tickets: int = Field(..., description="Total tickets in period")
    resolved_tickets: int = Field(..., description="Resolved tickets in period")
    pending_tickets: int = Field(..., description="Pending tickets in period")
    escalated_tickets: int = Field(..., description="Escalated tickets in period")
    avg_resolution_time_hrs: float = Field(..., description="Average resolution time in hours")
    avg_response_time_min: float = Field(..., description="Average response time in minutes")
    customer_satisfaction_score: float = Field(
        ..., description="Overall customer satisfaction index (0-5 or percentage)"
    )
    ai_confidence_score: float = Field(
        ..., description="Average confidence score from AI classifications and intents"
    )
    intent_distribution: dict[str, int] = Field(
        ..., description="Count distribution of different ticket intents"
    )
    sentiment_distribution: dict[str, int] = Field(
        ..., description="Count distribution of customer sentiments"
    )
    token_usage: TokenUsageMetrics = Field(..., description="LLM token consumption breakdown")
    cost: CostMetrics = Field(..., description="Cost metrics in USD")
    rag: RAGMetrics = Field(..., description="RAG retrieval and knowledge base metrics")
    agent_performance: list[AgentPerformanceDetail] = Field(
        ..., description="Performance metrics breakdown per agent"
    )
    system_health: SystemHealthMetrics = Field(..., description="Overall system health status")
