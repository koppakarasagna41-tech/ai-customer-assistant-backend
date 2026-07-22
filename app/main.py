import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.notifications import router as notification_router
from app.api.v1.attachments import router as attachment_router
from app.api.v1.agents import router as agent_router
from app.api.v1.activity_logs import (
    router as activity_logs_router,
)
from app.api.v1.ai_escalation_logic import (
    router as ai_escalation_logic_router,
)
from app.api.v1.ai_confidence_score import (
    router as ai_confidence_score_router,
)
from app.api.v1.audit_logs import (
    router as audit_logs_router,
)
from app.api.v1.ai_conversation_history import (
    router as ai_conversation_history_router,
)
from app.api.v1.ai_knowledge_base import (
    router as ai_knowledge_base_router,
)
from app.api.v1.ai_priority_prediction import (
    router as ai_priority_prediction_router,
)
from app.api.v1.ai_ticket_classification import (
    router as ai_ticket_classification_router,
)
from app.api.v1.user_preferences import (
    router as user_preferences_router,
)
from app.api.v1.dashboard import (
    router as dashboard_router,
)


from app.api.v1.refresh_tokens import (
    router as refresh_tokens_router,
)

from app.api.v1.router import api_router
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.ai_security import AISecurityMiddleware
from app.middleware.request_validator import RequestValidatorMiddleware
from app.schemas.error import ErrorDetail, ErrorResponse
from app.api.v1.assignment_history import (
    router as assignment_history_router,
)
from app.api.v1.ai_suggested_response import (
    router as ai_suggested_response_router,
)
from app.api.v1.ai_prompt_management import (
    router as ai_prompt_management_router,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format=(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"module": "%(module)s", "message": "%(message)s"}'
    ),
)
logger = logging.getLogger("enterprise_backend")

# Create FastAPI application instance
app = FastAPI(
    title="Enterprise AI Support Platform API",
    description=(
        "Enterprise-grade resilient AI support system with advanced "
        "security, RAG, and monitoring."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS configuration
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://ais-dev-opjdsuxw3p6deotmhqvdse-38002326166.asia-southeast1.run.app",
    "https://ais-pre-opjdsuxw3p6deotmhqvdse-38002326166.asia-southeast1.run.app",
]
# Support dynamic frontend URL if specified in environment
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Specific allowed HTTP methods
allowed_methods = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# Specific allowed headers
allowed_headers = [
    "Accept",
    "Accept-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-CSRF-Token",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# Security and performance middlewares
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=(
        ["*"]
        if os.getenv("ENV") != "production"
        else ["localhost", "*.run.app", "*.render.com", "*.vercel.app"]
    ),
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    RateLimiterMiddleware,
    requests_per_minute=100,
    excluded_paths=["/docs", "/redoc", "/openapi.json", "/health"],
)
app.add_middleware(RequestValidatorMiddleware)
app.add_middleware(AISecurityMiddleware)


# Root endpoint for checking server state
@app.get("/", tags=["Health"])
async def read_root():
    return {
        "success": True,
        "message": "Enterprise AI Customer Support Suite Backend is operational.",
        "documentation": "/docs",
    }


# Include API Router under /api/v1
app.include_router(api_router, prefix="/api/v1")
app.include_router(
    ai_escalation_logic_router,
    prefix="/api/v1/ai-escalation-logic",
    tags=["AI Escalation Logic"],
)
app.include_router(
    ai_prompt_management_router,
    prefix="/api/v1/ai-prompt-management",
    tags=["AI Prompt Management"],
)

app.include_router(
    ai_knowledge_base_router,
    prefix="/api/v1/ai-knowledge-base",
    tags=["AI Knowledge Base"],
)
app.include_router(
    ai_conversation_history_router,
    prefix="/api/v1/ai-conversation-history",
    tags=["AI Conversation History"],
)
app.include_router(
    ai_suggested_response_router,
    prefix="/api/v1/ai-suggested-response",
    tags=["AI Suggested Response"],
)
app.include_router(
    ai_priority_prediction_router,
    prefix="/api/v1/ai-priority-prediction",
    tags=["AI Priority Prediction"],
)
app.include_router(
    ai_ticket_classification_router,
    prefix="/api/v1/ai-ticket-classification",
    tags=["AI Ticket Classification"],
)
app.include_router(
    user_preferences_router,
    prefix="/api/v1/user-preferences",
    tags=["User Preferences"],
)
app.include_router(
    refresh_tokens_router,
    prefix="/api/v1/refresh-tokens",
    tags=["Refresh Tokens"],
)
app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)
app.include_router(
    audit_logs_router,
    prefix="/api/v1/audit-logs",
    tags=["Audit Logs"],
)
app.include_router(
    activity_logs_router,
    prefix="/api/v1/activity-logs",
    tags=["Activity Logs"],
)
app.include_router(
    ai_confidence_score_router,
    prefix="/api/v1/ai-confidence-score",
    tags=["AI Confidence Score"],
)
app.include_router(
    assignment_history_router,
    prefix="/api/v1/assignment-history",
    tags=["Assignment History"],
)
app.include_router(
    agent_router,
    prefix="/api/v1/agents",
    tags=["Agents"],
)
app.include_router(
    attachment_router,
    prefix="/api/v1/attachments",
    tags=["Attachments"],
)
app.include_router(
    notification_router,
    prefix="/api/v1/notifications",
    tags=["Notifications"],
)

# Standard Exception Handlers conforming to ErrorResponse schema
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors and "loc" in errors[0] and errors[0]["loc"] else None
    msg = errors[0]["msg"] if errors else "Validation failed"

    error_detail = ErrorDetail(
        code="VALIDATION_ERROR",
        message=f"Request validation failed: {msg}",
        field=str(field) if field else None,
    )
    response_content = ErrorResponse(success=False, error=error_detail).dict()

    logger.warning(f"Validation error: {errors}")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_content)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_detail = ErrorDetail(code=f"HTTP_{exc.status_code}", message=exc.detail, field=None)
    response_content = ErrorResponse(success=False, error=error_detail).dict()

    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content=response_content)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred. Please contact system support.",
        field=None,
    )
    response_content = ErrorResponse(success=False, error=error_detail).dict()

    logger.error(f"Unhandled server exception: {exc!s}", exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_content)


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Enterprise AI Support Backend Gateway...")
    logger.info("CORS policies, LLM pipelines, and memory caches loaded successfully.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Enterprise AI Support Backend Gateway...")
