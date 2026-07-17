from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TicketTimelineEvent(BaseModel):
    event_id: str
    event_type: (
        str  # created, status_updated, priority_updated, agent_assigned, commented, escalated
    )
    actor: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TicketComment(BaseModel):
    comment_id: str
    author: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Ticket(BaseModel):
    ticket_id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    assigned_agent_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    timeline: list[TicketTimelineEvent] = Field(default_factory=list)
    comments: list[TicketComment] = Field(default_factory=list)
