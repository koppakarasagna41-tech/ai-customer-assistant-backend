from pydantic import BaseModel, Field

class ConfidenceResponse(BaseModel):
    overall_confidence: float = Field(..., description="Combined confidence score across all models/services")
    status: str = Field(..., description="Confidence status level: HIGH, MEDIUM, LOW")
