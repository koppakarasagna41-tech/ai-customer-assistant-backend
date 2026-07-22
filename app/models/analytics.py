from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Analytics(BaseModel):
    id: int | None = None
    total_tickets: int | None = None
    resolved_tickets: int | None = None
    pending_tickets: int | None = None
    escalated_tickets: int | None = None
    avg_resolution_time_hrs: float | None = None
    avg_response_time_min: float | None = None
    customer_satisfaction_score: float | None = None
    ai_confidence_score: float | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
