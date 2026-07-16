from pydantic import BaseModel, Field
from typing import List

class ClassificationDetail(BaseModel):
    category: str = Field(..., description="The ticket category classification")
    confidence: float = Field(..., description="Confidence score of this classification")

class ClassificationResponse(BaseModel):
    classifications: List[ClassificationDetail] = Field(..., description="Classified ticket categories sorted by confidence")
