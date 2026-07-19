from datetime import datetime

from pydantic import BaseModel, Field


class RiskEvent(BaseModel):
    id: str
    timestamp: datetime
    prompt_snippet: str
    risk_type: str
    severity: str
    risk_score: float
    ip_address: str | None = None
    user_id: str | None = None


class RiskSummary(BaseModel):
    total_scans: int
    blocked_queries: int
    risk_distributions: dict[str, int] = Field(default_factory=dict)
    critical_alerts: int
    average_risk_score: float
    recent_events: list[RiskEvent]
