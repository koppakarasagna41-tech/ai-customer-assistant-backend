from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PromptEvaluationRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt text to evaluate")
    context_type: Optional[str] = Field("chat", description="Optional context type (chat, rag, document)")

class NormalizationDetails(BaseModel):
    original_length: int
    cleaned_length: int
    unicode_normalized: bool
    hidden_chars_removed: int

class InjectionAnalysis(BaseModel):
    detected: bool
    confidence: float
    threat_type: Optional[str] = None
    matched_pattern: Optional[str] = None

class JailbreakAnalysis(BaseModel):
    detected: bool
    confidence: float
    threat_type: Optional[str] = None
    matched_pattern: Optional[str] = None

class PromptEvaluationResult(BaseModel):
    is_safe: bool
    risk_score: float = Field(..., description="Risk score between 0.0 and 1.0")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    normalization: NormalizationDetails
    injection_analysis: InjectionAnalysis
    jailbreak_analysis: JailbreakAnalysis
    sanitized_prompt: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
