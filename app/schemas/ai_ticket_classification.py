from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AITicketClassificationCreate(BaseModel):
    ticket_id: str
    predicted_category: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    raw_response: str | None = None


class AITicketClassificationUpdate(BaseModel):
    predicted_category: str | None = None
    confidence_score: float | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    raw_response: str | None = None


class AITicketClassificationResponse(BaseModel):
    id: int
    ticket_id: str
    predicted_category: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    raw_response: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)