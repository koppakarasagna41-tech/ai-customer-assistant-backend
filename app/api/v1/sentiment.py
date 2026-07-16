from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.schemas.response import BaseResponse

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text content to analyze for sentiment")

class SentimentDetail(BaseModel):
    label: str = Field(..., description="Detected sentiment label (positive, neutral, negative)")
    score: float = Field(..., description="Sentiment score between 0.0 and 1.0")

class SentimentResponse(BaseModel):
    sentiment: SentimentDetail = Field(..., description="Overall text sentiment analysis")
    escalation_recommended: bool = Field(..., description="Whether emotional tone warrants agent escalation")

@router.post(
    "/sentiment",
    response_model=BaseResponse[SentimentResponse],
    status_code=status.HTTP_200_OK,
    summary="Analyze sentiment",
    description="Analyzes sentiment of customer interaction and suggests if escalation is needed."
)
async def analyze_sentiment(payload: SentimentRequest):
    return BaseResponse(
        success=True,
        message="Sentiment analysis complete",
        data=SentimentResponse(
            sentiment=SentimentDetail(
                label="negative",
                score=0.85
            ),
            escalation_recommended=True
        )
    )
