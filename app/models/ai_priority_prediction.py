from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIPriorityPrediction(BaseModel):
    id: int
    ticket_id: str
    predicted_priority: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    raw_response: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)