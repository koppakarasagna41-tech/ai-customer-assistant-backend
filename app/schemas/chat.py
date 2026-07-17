from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import UserContext
from app.schemas.message import Message


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message")
    history: list[Message] | None = Field(
        default_factory=list, description="Previous conversation history"
    )
    context: UserContext | None = Field(None, description="User context information")
    stream: bool | None = Field(False, description="Whether to stream the response (optional)")


class ChatMetadata(BaseModel):
    sentiment: str = Field("neutral", description="Detected user sentiment")
    category: str | None = Field(
        None, description="Detected category (e.g., billing, general, account)"
    )
    urgency: str | None = Field("medium", description="Estimated urgency level")
    entities: dict[str, Any] = Field(
        default_factory=dict, description="Extracted entities like ticket IDs, order numbers, etc."
    )
    token_usage: dict[str, int] = Field(
        default_factory=dict, description="Token usage details (input, output, total)"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's generated response")
    intent: str | None = Field(None, description="Detected user intent")
    suggested_actions: list[str] = Field(
        default_factory=list, description="Follow-up action suggestions"
    )
    metadata: ChatMetadata | None = Field(None, description="Extracted semantic metadata")
    summary: str | None = Field(None, description="Updated summary of the conversation so far")
