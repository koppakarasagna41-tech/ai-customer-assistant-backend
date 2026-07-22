from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIConfidenceScoreCreate(BaseModel):
    ticket_id: str
    confidence_score: float
    prediction_type: str
    model_name: str | None = None


class AIConfidenceScoreUpdate(BaseModel):
    confidence_score: float | None = None
    prediction_type: str | None = None
    model_name: str | None = None


class AIConfidenceScoreResponse(BaseModel):
    id: int
    ticket_id: str
    confidence_score: float
    prediction_type: str
    model_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)