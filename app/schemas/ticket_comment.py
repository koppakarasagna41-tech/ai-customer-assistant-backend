from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCommentCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class TicketCommentUpdate(BaseModel):
    author: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = Field(None, min_length=1)


class TicketCommentResponse(BaseModel):
    comment_id: str
    ticket_id: str
    author: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
