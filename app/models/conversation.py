from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Conversation(BaseModel):
    session_id: str
    user_id: str | None = None
    summary: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    session_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
