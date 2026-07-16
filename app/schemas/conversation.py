from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.schemas.message import Message

class ConversationState(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    messages: List[Message] = Field(default_factory=list, description="All messages in the conversation")
    summary: Optional[str] = Field(None, description="Summary of past conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session-level metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
