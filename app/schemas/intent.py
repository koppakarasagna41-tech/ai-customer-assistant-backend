from pydantic import BaseModel, Field


class IntentDetail(BaseModel):
    intent: str = Field(..., description="The main intent category detected")
    confidence: float = Field(..., description="Confidence score of the detected intent")


class IntentResponse(BaseModel):
    intents: list[IntentDetail] = Field(..., description="Detected intents sorted by confidence")
