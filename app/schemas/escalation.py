from pydantic import BaseModel, Field


class EscalationResponse(BaseModel):
    escalation_score: float = Field(..., description="Probability of escalation from 0.0 to 1.0")
    escalation_recommended: bool = Field(
        ..., description="Whether emotional tone or high urgency warrants escalation"
    )
    reasons: list[str] = Field(
        default_factory=list, description="List of reasons for escalation recommendations"
    )
