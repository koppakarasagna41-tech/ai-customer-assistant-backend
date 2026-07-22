from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TicketTimelineEntry(BaseModel):
    event_id: str
    ticket_id: str
    event_type: str
    actor: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
