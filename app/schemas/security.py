from datetime import datetime

from pydantic import BaseModel, Field


class PromptEvaluationRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt text to evaluate")
    context_type: str | None = Field(
        "chat", description="Optional context type (chat, rag, document)"
    )


class NormalizationDetails(BaseModel):
    original_length: int
    cleaned_length: int
    unicode_normalized: bool
    hidden_chars_removed: int


class InjectionAnalysis(BaseModel):
    detected: bool
    confidence: float
    threat_type: str | None = None
    matched_pattern: str | None = None


class JailbreakAnalysis(BaseModel):
    detected: bool
    confidence: float
    threat_type: str | None = None
    matched_pattern: str | None = None


class PromptEvaluationResult(BaseModel):
    is_safe: bool
    risk_score: float = Field(..., description="Risk score between 0.0 and 1.0")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    normalization: NormalizationDetails
    injection_analysis: InjectionAnalysis
    jailbreak_analysis: JailbreakAnalysis
    sanitized_prompt: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
