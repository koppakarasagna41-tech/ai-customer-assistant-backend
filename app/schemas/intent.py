from pydantic import BaseModel, Field
from typing import List

class IntentDetail(BaseModel):
    intent: str = Field(..., description="The main intent category detected")
    confidence: float = Field(..., description="Confidence score of the detected intent")

class IntentResponse(BaseModel):
    intents: List[IntentDetail] = Field(..., description="Detected intents sorted by confidence")
