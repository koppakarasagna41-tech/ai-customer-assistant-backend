from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.message import Message
from app.schemas.common import UserContext

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message")
    history: Optional[List[Message]] = Field(default_factory=list, description="Previous conversation history")
    context: Optional[UserContext] = Field(None, description="User context information")
    stream: Optional[bool] = Field(False, description="Whether to stream the response (optional)")

class ChatMetadata(BaseModel):
    sentiment: str = Field("neutral", description="Detected user sentiment")
    category: Optional[str] = Field(None, description="Detected category (e.g., billing, general, account)")
    urgency: Optional[str] = Field("medium", description="Estimated urgency level")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities like ticket IDs, order numbers, etc.")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage details (input, output, total)")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's generated response")
    intent: Optional[str] = Field(None, description="Detected user intent")
    suggested_actions: List[str] = Field(default_factory=list, description="Follow-up action suggestions")
    metadata: Optional[ChatMetadata] = Field(None, description="Extracted semantic metadata")
    summary: Optional[str] = Field(None, description="Updated summary of the conversation so far")
