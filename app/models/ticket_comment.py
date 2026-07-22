from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketComment(BaseModel):
    comment_id: str
    ticket_id: str
    author: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
