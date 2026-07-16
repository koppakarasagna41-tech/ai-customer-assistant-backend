from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.schemas.response import BaseResponse
from app.services.analysis_pipeline import get_analysis_pipeline, AnalysisPipeline

router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Message text to run through the AI Intelligence Layer")

@router.post(
    "/analyze",
    response_model=BaseResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Analyze message through AI Intelligence Layer",
    description="Runs the dual-stage analysis pipeline on user text, including intent detection, ticket classification, sentiment, urgency, risk, and response recommendations."
)
async def analyze_message(
    payload: AnalysisRequest,
    pipeline: AnalysisPipeline = Depends(get_analysis_pipeline)
):
    result = await pipeline.analyze(payload.text)
    return BaseResponse(
        success=True,
        message="Message analysis complete",
        data=result
    )
