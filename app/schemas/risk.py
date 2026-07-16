from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RiskEvent(BaseModel):
    id: str
    timestamp: datetime
    prompt_snippet: str
    risk_type: str
    severity: str
    risk_score: float
    ip_address: Optional[str] = None
    user_id: Optional[str] = None

class RiskSummary(BaseModel):
    total_scanned: int
    malicious_blocked: int
    critical_alerts: int
    average_risk_score: float
    recent_events: List[RiskEvent]
