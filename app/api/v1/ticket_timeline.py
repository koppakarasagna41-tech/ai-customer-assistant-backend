from fastapi import APIRouter, Depends, Path, status

from app.schemas.ticket_timeline import TicketTimelineEntryCreate, TicketTimelineEntryResponse
from app.services.ticket_timeline_service import TicketTimelineService, get_ticket_timeline_service

router = APIRouter()


@router.post(
    "/tickets/{ticket_id}/timeline",
    response_model=TicketTimelineEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket_timeline_entry(
    payload: TicketTimelineEntryCreate,
    ticket_id: str = Path(..., description="Ticket ID"),
    service: TicketTimelineService = Depends(get_ticket_timeline_service),
):
    return await service.create_event(ticket_id, payload)


@router.get(
    "/tickets/{ticket_id}/timeline",
    response_model=list[TicketTimelineEntryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_ticket_timeline(
    ticket_id: str = Path(..., description="Ticket ID"),
    service: TicketTimelineService = Depends(get_ticket_timeline_service),
):
    return await service.get_timeline(ticket_id)
