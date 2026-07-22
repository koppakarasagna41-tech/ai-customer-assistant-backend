from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_conversation_history import (
    AIConversationHistoryCreate,
    AIConversationHistoryResponse,
    AIConversationHistoryUpdate,
)
from app.services.ai_conversation_history_service import (
    AIConversationHistoryService,
    get_ai_conversation_history_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIConversationHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    data: AIConversationHistoryCreate,
    service: AIConversationHistoryService = Depends(get_ai_conversation_history_service),
):
    return await service.create_conversation(data)


@router.get(
    "/{ticket_id}",
    response_model=list[AIConversationHistoryResponse],
)
async def get_conversations(
    ticket_id: str,
    service: AIConversationHistoryService = Depends(get_ai_conversation_history_service),
):
    return await service.get_conversations(ticket_id)


@router.put(
    "/{conversation_id}",
    response_model=AIConversationHistoryResponse,
)
async def update_conversation(
    conversation_id: int,
    data: AIConversationHistoryUpdate,
    service: AIConversationHistoryService = Depends(get_ai_conversation_history_service),
):
    conversation = await service.update_conversation(
        conversation_id,
        data,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


@router.delete(
    "/{conversation_id}",
)
async def delete_conversation(
    conversation_id: int,
    service: AIConversationHistoryService = Depends(get_ai_conversation_history_service),
):
    deleted = await service.delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {"message": "Conversation deleted successfully"}
