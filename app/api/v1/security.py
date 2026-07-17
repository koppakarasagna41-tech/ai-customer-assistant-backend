from fastapi import APIRouter, Depends, status

from app.schemas.moderation import ContentModerationRequest, ContentModerationResult
from app.schemas.response import BaseResponse
from app.schemas.risk import RiskSummary
from app.schemas.security import PromptEvaluationRequest, PromptEvaluationResult
from app.services.security_service import SecurityService, get_security_service

router = APIRouter()


@router.post(
    "/security/validate",
    response_model=BaseResponse[PromptEvaluationResult],
    status_code=status.HTTP_200_OK,
    summary="Validate and scan prompt for vulnerabilities",
    description=(
        "Scan an incoming user prompt for injection, jailbreaks, hidden "
        "control character exploits, and generate detailed risk metadata."
    ),
)
async def validate_prompt_endpoint(
    payload: PromptEvaluationRequest,
    security_service: SecurityService = Depends(get_security_service),
):
    result = security_service.inspect_incoming_prompt(payload.prompt)
    return BaseResponse(success=True, message="Prompt security validation complete.", data=result)


@router.post(
    "/security/moderate",
    response_model=BaseResponse[ContentModerationResult],
    status_code=status.HTTP_200_OK,
    summary="Perform policy content moderation",
    description=(
        "Check content against hate speech, harassment, self-harm, sexual "
        "content, violence, and malicious hacking patterns."
    ),
)
async def moderate_content_endpoint(
    payload: ContentModerationRequest,
    security_service: SecurityService = Depends(get_security_service),
):
    result = security_service.check_content_moderation(payload.content)
    return BaseResponse(success=True, message="Content moderation analysis complete.", data=result)


@router.get(
    "/security/analytics",
    response_model=BaseResponse[RiskSummary],
    status_code=status.HTTP_200_OK,
    summary="Retrieve security event analytics",
    description=(
        "Fetch real-time statistics regarding blocked queries, risk types, "
        "severity distributions, and a history of recent threat events."
    ),
)
async def get_security_analytics_endpoint(
    security_service: SecurityService = Depends(get_security_service),
):
    analytics = security_service.get_security_analytics()
    return BaseResponse(
        success=True, message="Security analytics summary compiled successfully.", data=analytics
    )
