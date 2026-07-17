from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="Role of the sender (e.g., user, assistant, system)")
    content: str = Field(..., description="The message text content")
    timestamp: datetime | None = Field(
        default_factory=datetime.utcnow, description="Timestamp of the message"
    )
