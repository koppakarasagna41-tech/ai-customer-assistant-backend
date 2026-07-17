import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.middleware.ai_security import AISecurityMiddleware
from app.middleware.request_validator import RequestValidatorMiddleware
from app.schemas.error import ErrorDetail, ErrorResponse

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
    "https://vercel.com",
]
# Support dynamic frontend URL if specified in environment
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
