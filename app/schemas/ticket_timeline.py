from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TicketTimelineEntryCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    actor: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class TicketTimelineEntryResponse(BaseModel):
    event_id: str
    ticket_id: str
    event_type: str
    actor: str
    description: str
    timestamp: datetime
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
