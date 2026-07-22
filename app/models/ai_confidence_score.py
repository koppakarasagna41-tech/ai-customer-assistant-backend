from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIConfidenceScore(BaseModel):
    id: int
    ticket_id: str
    confidence_score: float
    prediction_type: str
    model_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
