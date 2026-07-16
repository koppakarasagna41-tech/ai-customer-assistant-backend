from fastapi import APIRouter, status, Depends, HTTPException
from typing import Optional
from app.schemas.response import BaseResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, get_chat_service

router = APIRouter()

@router.post(
    "/chat",
    response_model=BaseResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Send message to AI assistant",
    description="Processes user input and returns an AI generated response with context and metadata."
)
async def process_chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    try:
        user_id = payload.context.user_id if payload.context else None
        session_id = payload.context.session_id if (payload.context and payload.context.session_id) else "default-session"
        client_metadata = payload.context.metadata if payload.context else None

        chat_response = await service.process_chat_message(
            message_text=payload.message,
            session_id=session_id,
            user_id=user_id,
            client_metadata=client_metadata
        )
        return BaseResponse(
            success=True,
            message="Chat processed successfully",
            data=chat_response
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the chat: {str(e)}"
        )
