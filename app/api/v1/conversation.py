from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationState
from app.services.conversation_service import ConversationService, get_conversation_service

router = APIRouter()


@router.get(
    "/conversations",
    response_model=list[Conversation],
    status_code=status.HTTP_200_OK,
)
async def list_conversations(
    user_id: str | None = Query(None, description="Filter conversations by user ID"),
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.list_conversations(user_id)


@router.post(
    "/conversations",
    response_model=Conversation,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    data: ConversationState,
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.create_conversation(data)


@router.get(
    "/conversations/{session_id}",
    response_model=Conversation,
    status_code=status.HTTP_200_OK,
)
async def get_conversation(
    session_id: str = Path(..., description="Conversation session ID"),
    service: ConversationService = Depends(get_conversation_service),
):
    conversation = await service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.patch(
    "/conversations/{session_id}",
    response_model=Conversation,
    status_code=status.HTTP_200_OK,
)
async def update_conversation(
    data: ConversationState,
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.update_conversation(data)


@router.delete(
    "/conversations/{session_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_conversation(
    session_id: str = Path(..., description="Conversation session ID"),
    service: ConversationService = Depends(get_conversation_service),
):
    deleted = await service.delete_conversation(session_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return {"success": True, "message": "Conversation deleted successfully"}
