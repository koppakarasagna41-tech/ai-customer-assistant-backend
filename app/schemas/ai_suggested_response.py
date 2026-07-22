from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AISuggestedResponseCreate(BaseModel):
    ticket_id: str
    suggested_response: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    status: str = "generated"


class AISuggestedResponseUpdate(BaseModel):
    suggested_response: str | None = None
    confidence_score: float | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    status: str | None = None


class AISuggestedResponseResponse(BaseModel):
    id: int
    ticket_id: str
    suggested_response: str
    confidence_score: float
    model_name: str
    prompt_version: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)