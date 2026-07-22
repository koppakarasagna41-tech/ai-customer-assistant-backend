from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.schemas.ticket_comment import TicketCommentCreate, TicketCommentResponse
from app.services.ticket_comment_service import TicketCommentService, get_ticket_comment_service

router = APIRouter()


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_comment(
    payload: TicketCommentCreate,
    ticket_id: str = Path(..., description="Ticket ID"),
    service: TicketCommentService = Depends(get_ticket_comment_service),
):
    return await service.create_comment(ticket_id, payload)


@router.get(
    "/tickets/{ticket_id}/comments",
    response_model=list[TicketCommentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_ticket_comments(
    ticket_id: str = Path(..., description="Ticket ID"),
    service: TicketCommentService = Depends(get_ticket_comment_service),
):
    return await service.get_comments(ticket_id)


@router.delete(
    "/tickets/{ticket_id}/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_ticket_comment(
    ticket_id: str = Path(..., description="Ticket ID"),
    comment_id: str = Path(..., description="Comment ID"),
    service: TicketCommentService = Depends(get_ticket_comment_service),
):
    deleted = await service.delete_comment(comment_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return {"success": True, "message": "Comment deleted successfully"}
