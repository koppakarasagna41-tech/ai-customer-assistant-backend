from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    role: str = Field(..., description="Role of the sender (e.g., user, assistant, system)")
    content: str = Field(..., description="The message text content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of the message")
