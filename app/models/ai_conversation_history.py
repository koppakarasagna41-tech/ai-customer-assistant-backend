from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIConversationHistory(BaseModel):
    id: int
    ticket_id: str
    user_message: str
    ai_response: str
    model_name: str | None = None
    conversation_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
