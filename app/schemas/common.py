from typing import Any

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: str | None = Field(None, description="Unique identifier for the user")
    session_id: str | None = Field(None, description="Session identifier for tracking conversation")
    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional context or metadata"
    )
