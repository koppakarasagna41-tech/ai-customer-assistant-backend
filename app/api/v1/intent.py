from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import List
from app.schemas.response import BaseResponse

router = APIRouter()

class IntentRequest(BaseModel):
    text: str = Field(..., description="User query to detect intent from")

class DetectedIntent(BaseModel):
    intent: str = Field(..., description="Main intent category detected")
    confidence: float = Field(..., description="Confidence score")

class IntentResponse(BaseModel):
    intents: List[DetectedIntent] = Field(..., description="Detected intents sorted by confidence")

@router.post(
    "/intent",
    response_model=BaseResponse[IntentResponse],
    status_code=status.HTTP_200_OK,
    summary="Detect message intent",
    description="Detects user intent from conversational query input."
)
async def detect_intent(payload: IntentRequest):
    return BaseResponse(
        success=True,
        message="Intent detection complete",
        data=IntentResponse(
            intents=[
                DetectedIntent(intent="billing_issue", confidence=0.89),
                DetectedIntent(intent="refund_request", confidence=0.11)
            ]
        )
    )
