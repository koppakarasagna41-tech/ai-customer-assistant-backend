from datetime import datetime

from pydantic import BaseModel


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
    total_scanned: int
    malicious_blocked: int
    critical_alerts: int
    average_risk_score: float
    recent_events: list[RiskEvent]
