from pydantic import BaseModel, Field

class SentimentDetail(BaseModel):
    label: str = Field(..., description="Detected sentiment label (positive, neutral, negative)")
    score: float = Field(..., description="Sentiment score between 0.0 and 1.0")

class SentimentResponse(BaseModel):
    sentiment: SentimentDetail = Field(..., description="Overall text sentiment analysis")
    escalation_recommended: bool = Field(..., description="Whether emotional tone warrants agent escalation")
