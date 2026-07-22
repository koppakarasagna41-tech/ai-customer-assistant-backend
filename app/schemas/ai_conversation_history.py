from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIConversationHistoryCreate(BaseModel):
    ticket_id: str
    user_message: str
    ai_response: str
    model_name: str | None = None
    conversation_id: str | None = None


class AIConversationHistoryUpdate(BaseModel):
    user_message: str | None = None
    ai_response: str | None = None
    model_name: str | None = None
    conversation_id: str | None = None


class AIConversationHistoryResponse(BaseModel):
    id: int
    ticket_id: str
    user_message: str
    ai_response: str
    model_name: str | None = None
    conversation_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)