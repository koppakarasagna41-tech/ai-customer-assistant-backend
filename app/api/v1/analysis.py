from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.schemas.response import BaseResponse
from app.services.analysis_pipeline import AnalysisPipeline, get_analysis_pipeline

router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Message text to run through the AI Intelligence Layer")


@router.post(
    "/analyze",
    response_model=BaseResponse[dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Analyze message through AI Intelligence Layer",
    description=(
        "Runs the dual-stage analysis pipeline on user text, including "
        "intent detection, ticket classification, sentiment, urgency, "
        "risk, and response recommendations."
    ),
)
async def analyze_message(
    payload: AnalysisRequest, pipeline: AnalysisPipeline = Depends(get_analysis_pipeline)
):
    result = await pipeline.analyze(payload.text)
    return BaseResponse(success=True, message="Message analysis complete", data=result)
