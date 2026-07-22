from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_ticket_classification import (
    AITicketClassificationCreate,
    AITicketClassificationResponse,
    AITicketClassificationUpdate,
)
from app.services.ai_ticket_classification_service import (
    AITicketClassificationService,
    get_ai_ticket_classification_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AITicketClassificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_classification(
    classification: AITicketClassificationCreate,
    service: AITicketClassificationService = Depends(
        get_ai_ticket_classification_service,
    ),
):
    return await service.create_classification(classification)


@router.get(
    "/{ticket_id}",
    response_model=AITicketClassificationResponse,
)
async def get_classification(
    ticket_id: str,
    service: AITicketClassificationService = Depends(
        get_ai_ticket_classification_service,
    ),
):
    classification = await service.get_classification(ticket_id)

    if classification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI ticket classification not found",
        )

    return classification


@router.put(
    "/{ticket_id}",
    response_model=AITicketClassificationResponse,
)
async def update_classification(
    ticket_id: str,
    classification: AITicketClassificationUpdate,
    service: AITicketClassificationService = Depends(
        get_ai_ticket_classification_service,
    ),
):
    updated = await service.update_classification(
        ticket_id,
        classification,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI ticket classification not found",
        )

    return updated


@router.delete(
    "/{ticket_id}",
)
async def delete_classification(
    ticket_id: str,
    service: AITicketClassificationService = Depends(
        get_ai_ticket_classification_service,
    ),
):
    deleted = await service.delete_classification(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI ticket classification not found",
        )

    return {
        "success": True,
        "message": "AI ticket classification deleted successfully",
    }