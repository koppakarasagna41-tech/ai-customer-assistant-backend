from app.schemas.moderation import ContentModerationResult
from app.schemas.risk import RiskEvent, RiskSummary
from app.schemas.security import PromptEvaluationResult
from app.services.content_moderator import ContentModerator, get_content_moderator
from app.services.output_filter import OutputFilter, get_output_filter
from app.services.prompt_validator import PromptValidator, get_prompt_validator
from app.services.security_logger import SecurityLogger, get_security_logger


class SecurityService:
    def __init__(
        self,
        validator: PromptValidator = None,
        output_filter: OutputFilter = None,
        moderator: ContentModerator = None,
        logger: SecurityLogger = None,
    ):
        self.validator = validator or get_prompt_validator()
        self.output_filter = output_filter or get_output_filter()
        self.moderator = moderator or get_content_moderator()
        self.logger = logger or get_security_logger()

    def inspect_incoming_prompt(
        self, prompt: str, user_id: str | None = None, ip: str | None = None
    ) -> PromptEvaluationResult:
        return self.validator.validate_prompt(prompt, user_id, ip)

    def inspect_outgoing_response(self, response_text: str) -> str:
        return self.output_filter.filter_response(response_text)

    def check_content_moderation(self, text: str) -> ContentModerationResult:
        return self.moderator.moderate(text)

    def get_security_analytics(self) -> RiskSummary:
        log_summary = self.logger.get_summary()
        recent_events = []
        for e in log_summary["recent_events"]:
            recent_events.append(
                RiskEvent(
                    id=e["id"],
                    timestamp=e["timestamp"],
                    prompt_snippet=e["prompt_snippet"],
                    risk_type=e["risk_type"],
                    severity=e["severity"],
                    risk_score=e["risk_score"],
                    ip_address=e["ip_address"],
                    user_id=e["user_id"],
                )
            )
        return RiskSummary(
            total_scanned=log_summary["total_scanned"],
            malicious_blocked=log_summary["malicious_blocked"],
            critical_alerts=log_summary["critical_alerts"],
            average_risk_score=log_summary["average_risk_score"],
            recent_events=recent_events,
        )


_global_security_service = SecurityService()


def get_security_service() -> SecurityService:
    return _global_security_service
