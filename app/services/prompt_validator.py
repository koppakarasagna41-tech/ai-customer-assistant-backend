from app.schemas.security import (
    InjectionAnalysis,
    JailbreakAnalysis,
    NormalizationDetails,
    PromptEvaluationResult,
)
from app.services.injection_detector import InjectionDetector, get_injection_detector
from app.services.jailbreak_detector import JailbreakDetector, get_jailbreak_detector
from app.services.prompt_sanitizer import PromptSanitizer, get_prompt_sanitizer
from app.services.security_logger import SecurityLogger, get_security_logger


class PromptValidator:
    def __init__(
        self,
        sanitizer: PromptSanitizer = None,
        jailbreak_detector: JailbreakDetector = None,
        injection_detector: InjectionDetector = None,
        security_logger: SecurityLogger = None,
    ):
        self.sanitizer = sanitizer or get_prompt_sanitizer()
        self.jailbreak_detector = jailbreak_detector or get_jailbreak_detector()
        self.injection_detector = injection_detector or get_injection_detector()
        self.security_logger = security_logger or get_security_logger()

    def validate_prompt(
        self, raw_prompt: str, user_id: str | None = None, ip: str | None = None
    ) -> PromptEvaluationResult:
        # 1. Normalization
        clean_prompt, norm_details = self.sanitizer.normalize(raw_prompt)

        # 2. Sanitize HTML/JS
        clean_prompt = self.sanitizer.sanitize(clean_prompt)

        # 3. Detect Jailbreak
        jb_detected, jb_conf, jb_type, jb_match = self.jailbreak_detector.detect(clean_prompt)

        # 4. Detect Injection
        inj_detected, inj_conf, inj_type, inj_match = self.injection_detector.detect(clean_prompt)

        # Risk assessment & scoring
        is_safe = True
        risk_score = 0.0
        severity = "LOW"
        risk_type = "none"

        if jb_detected:
            is_safe = False
            risk_score = max(risk_score, jb_conf)
            risk_type = jb_type

        if inj_detected:
            is_safe = False
            risk_score = max(risk_score, inj_conf)
            risk_type = inj_type

        # Map score to severity
        if risk_score >= 0.85:
            severity = "CRITICAL"
        elif risk_score >= 0.7:
            severity = "HIGH"
        elif risk_score >= 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Log event
        self.security_logger.log_scan(
            prompt=raw_prompt,
            is_safe=is_safe,
            risk_score=risk_score,
            severity=severity,
            risk_type=risk_type,
            user_id=user_id,
            ip=ip,
        )

        return PromptEvaluationResult(
            is_safe=is_safe,
            risk_score=risk_score,
            severity=severity,
            normalization=NormalizationDetails(**norm_details),
            injection_analysis=InjectionAnalysis(
                detected=inj_detected,
                confidence=inj_conf,
                threat_type=inj_type if inj_detected else None,
                matched_pattern=inj_match if inj_detected else None,
            ),
            jailbreak_analysis=JailbreakAnalysis(
                detected=jb_detected,
                confidence=jb_conf,
                threat_type=jb_type if jb_detected else None,
                matched_pattern=jb_match if jb_detected else None,
            ),
            sanitized_prompt=clean_prompt,
        )


_global_prompt_validator = PromptValidator()


def get_prompt_validator() -> PromptValidator:
    return _global_prompt_validator
