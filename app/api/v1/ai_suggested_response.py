from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_suggested_response import (
    AISuggestedResponseCreate,
    AISuggestedResponseResponse,
    AISuggestedResponseUpdate,
)
from app.services.ai_suggested_response_service import (
    AISuggestedResponseService,
    get_ai_suggested_response_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AISuggestedResponseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_response(
    response: AISuggestedResponseCreate,
    service: AISuggestedResponseService = Depends(
        get_ai_suggested_response_service,
    ),
):
    return await service.create_response(response)


@router.get(
    "/{ticket_id}",
    response_model=AISuggestedResponseResponse,
)
async def get_response(
    ticket_id: str,
    service: AISuggestedResponseService = Depends(
        get_ai_suggested_response_service,
    ),
):
    result = await service.get_response(ticket_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI suggested response not found",
        )

    return result


@router.put(
    "/{ticket_id}",
    response_model=AISuggestedResponseResponse,
)
async def update_response(
    ticket_id: str,
    response: AISuggestedResponseUpdate,
    service: AISuggestedResponseService = Depends(
        get_ai_suggested_response_service,
    ),
):
    updated = await service.update_response(
        ticket_id,
        response,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI suggested response not found",
        )

    return updated


@router.delete(
    "/{ticket_id}",
)
async def delete_response(
    ticket_id: str,
    service: AISuggestedResponseService = Depends(
        get_ai_suggested_response_service,
    ),
):
    deleted = await service.delete_response(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI suggested response not found",
        )

    return {
        "success": True,
        "message": "AI suggested response deleted successfully",
    }