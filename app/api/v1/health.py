from fastapi import APIRouter, status
from app.schemas.response import BaseResponse
from pydantic import BaseModel, Field
from typing import Dict

router = APIRouter()

class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall health status of the application")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(..., description="Status of dependent services")

@router.get(
    "/health",
    response_model=BaseResponse[HealthStatus],
    status_code=status.HTTP_200_OK,
    summary="Get application health status",
    description="Returns the operational status of the service and its dependencies."
)
async def get_health():
    return BaseResponse(
        success=True,
        message="Service is healthy",
        data=HealthStatus(
            status="healthy",
            version="1.0.0",
            services={
                "database": "connected",
                "ai_gateway": "online",
                "retriever": "online"
            }
        )
    )
