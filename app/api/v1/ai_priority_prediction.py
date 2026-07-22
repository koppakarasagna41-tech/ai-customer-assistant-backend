from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_priority_prediction import (
    AIPriorityPredictionCreate,
    AIPriorityPredictionResponse,
    AIPriorityPredictionUpdate,
)
from app.services.ai_priority_prediction_service import (
    AIPriorityPredictionService,
    get_ai_priority_prediction_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIPriorityPredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prediction(
    prediction: AIPriorityPredictionCreate,
    service: AIPriorityPredictionService = Depends(
        get_ai_priority_prediction_service,
    ),
):
    return await service.create_prediction(prediction)


@router.get(
    "/{ticket_id}",
    response_model=AIPriorityPredictionResponse,
)
async def get_prediction(
    ticket_id: str,
    service: AIPriorityPredictionService = Depends(
        get_ai_priority_prediction_service,
    ),
):
    prediction = await service.get_prediction(ticket_id)

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI priority prediction not found",
        )

    return prediction


@router.put(
    "/{ticket_id}",
    response_model=AIPriorityPredictionResponse,
)
async def update_prediction(
    ticket_id: str,
    prediction: AIPriorityPredictionUpdate,
    service: AIPriorityPredictionService = Depends(
        get_ai_priority_prediction_service,
    ),
):
    updated = await service.update_prediction(
        ticket_id,
        prediction,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI priority prediction not found",
        )

    return updated


@router.delete(
    "/{ticket_id}",
)
async def delete_prediction(
    ticket_id: str,
    service: AIPriorityPredictionService = Depends(
        get_ai_priority_prediction_service,
    ),
):
    deleted = await service.delete_prediction(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI priority prediction not found",
        )

    return {
        "success": True,
        "message": "AI priority prediction deleted successfully",
    }