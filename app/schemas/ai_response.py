from typing import Any

from pydantic import BaseModel, Field


class StructuredAIResponse(BaseModel):
    response: str = Field(..., description="The main text response to the user")
    intent: str = Field(
        ...,
        description="Detected user intent (e.g., greet, create_ticket, check_status, ask_question)",
    )
    sentiment: str = Field(
        "neutral", description="Detected sentiment of the user (positive, neutral, negative)"
    )
    category: str = Field(
        "general",
        description="Detected issue category (billing, account, hardware, software, general)",
    )
    urgency: str = Field(
        "medium", description="Estimated urgency level (low, medium, high, critical)"
    )
    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities like ticket_id, order_id, product_name",
    )
    suggested_actions: list[str] = Field(
        default_factory=list, description="List of 1 to 3 recommended follow-up actions"
    )
