from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AISuggestedResponse(BaseModel):
    id: int
    ticket_id: str
    suggested_response: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)