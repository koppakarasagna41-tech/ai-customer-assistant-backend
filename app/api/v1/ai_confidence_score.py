from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_confidence_score import (
    AIConfidenceScoreCreate,
    AIConfidenceScoreResponse,
    AIConfidenceScoreUpdate,
)
from app.services.ai_confidence_score_service import (
    AIConfidenceScoreService,
    get_ai_confidence_score_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIConfidenceScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_confidence_score(
    data: AIConfidenceScoreCreate,
    service: AIConfidenceScoreService = Depends(get_ai_confidence_score_service),
):
    return await service.create_confidence_score(data)


@router.get(
    "/{ticket_id}",
    response_model=list[AIConfidenceScoreResponse],
)
async def get_confidence_scores(
    ticket_id: str,
    service: AIConfidenceScoreService = Depends(get_ai_confidence_score_service),
):
    return await service.get_confidence_scores(ticket_id)


@router.put(
    "/{confidence_id}",
    response_model=AIConfidenceScoreResponse,
)
async def update_confidence_score(
    confidence_id: int,
    data: AIConfidenceScoreUpdate,
    service: AIConfidenceScoreService = Depends(get_ai_confidence_score_service),
):
    confidence = await service.update_confidence_score(
        confidence_id,
        data,
    )

    if not confidence:
        raise HTTPException(
            status_code=404,
            detail="Confidence score not found",
        )

    return confidence


@router.delete(
    "/{confidence_id}",
)
async def delete_confidence_score(
    confidence_id: int,
    service: AIConfidenceScoreService = Depends(get_ai_confidence_score_service),
):
    deleted = await service.delete_confidence_score(confidence_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Confidence score not found",
        )

    return {"message": "Confidence score deleted successfully"}
