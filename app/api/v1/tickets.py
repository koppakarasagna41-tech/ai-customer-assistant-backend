from fastapi import APIRouter, status, Path, Query, Depends, HTTPException
from typing import Optional, List
from app.schemas.response import BaseResponse, PaginatedData
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketStatusUpdate,
    TicketPriorityUpdate, TicketAgentAssign, TicketCommentCreate,
    TicketDashboardStats
)
from app.schemas.filter import TicketFilterParams, SortOrder
from app.models.ticket import Ticket, TicketTimelineEvent, TicketComment
from app.services.ticket_service import TicketService, get_ticket_service

router = APIRouter()

@router.post(
    "/tickets/classify",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Classify ticket priority and category",
    description="Uses local heuristics to classify support tickets and suggest priority/category."
)
async def classify_ticket(payload: TicketCreate):
    # Standard dummy classification based on description keyword searches
    desc_lower = payload.description.lower()
    category = payload.category
    priority = payload.priority

    if "billing" in desc_lower or "invoice" in desc_lower or "payment" in desc_lower:
        category = "billing"
        priority = "high"
    elif "sso" in desc_lower or "saml" in desc_lower or "login" in desc_lower or "oauth" in desc_lower:
        category = "technical"
        priority = "urgent"

    return BaseResponse(
        success=True,
        message="Ticket classified",
        data={
            "category": category,
            "confidence": 0.89,
            "priority": priority
        }
    )

@router.post(
    "/tickets/create",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
    description="Creates a new customer support ticket in the system."
)
async def create_ticket(
    payload: TicketCreate,
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.create_ticket(payload)
        return BaseResponse(
            success=True,
            message="Ticket created successfully",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/tickets",
    response_model=BaseResponse[PaginatedData[Ticket]],
    status_code=status.HTTP_200_OK,
    summary="List, search, and filter tickets",
    description="Retrieves support tickets matching the specified filter criteria with support for pagination and sorting."
)
async def list_tickets(
    category: Optional[str] = Query(None, description="Filter by ticket category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_agent_id: Optional[str] = Query(None, description="Filter by assigned agent"),
    search_query: Optional[str] = Query(None, description="Search keyword matching title/description"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[SortOrder] = Query(SortOrder.DESC, description="Sort order direction"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: TicketService = Depends(get_ticket_service)
):
    filters = TicketFilterParams(
        category=category,
        priority=priority,
        status=status,
        assigned_agent_id=assigned_agent_id,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order
    )
    items, total = await service.list_tickets(filters, page=page, size=size)
    paginated = PaginatedData(
        items=items,
        total=total,
        page=page,
        size=size
    )
    return BaseResponse(
        success=True,
        message="Tickets retrieved successfully",
        data=paginated
    )

@router.get(
    "/tickets/stats/dashboard",
    response_model=BaseResponse[TicketDashboardStats],
    status_code=status.HTTP_200_OK,
    summary="Get ticket dashboard statistics",
    description="Retrieves the overall, status-wise, priority-wise, and category-wise ticket statistics."
)
async def get_dashboard_stats(service: TicketService = Depends(get_ticket_service)):
    stats = await service.get_dashboard_stats()
    return BaseResponse(
        success=True,
        message="Dashboard statistics retrieved",
        data=TicketDashboardStats(**stats)
    )

@router.get(
    "/tickets/{ticket_id}",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_200_OK,
    summary="Get ticket details",
    description="Retrieves a specific support ticket's details by ID including timeline events and comments."
)
async def get_ticket(
    ticket_id: str = Path(..., description="The ID of the ticket to fetch"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.get_ticket(ticket_id)
        return BaseResponse(
            success=True,
            message="Ticket retrieved successfully",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch(
    "/tickets/{ticket_id}",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_200_OK,
    summary="Update ticket metadata",
    description="Partially updates any fields of a specific ticket."
)
async def update_ticket(
    payload: TicketUpdate,
    ticket_id: str = Path(..., description="The ID of the ticket to update"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.update_ticket(ticket_id, payload, actor="agent")
        return BaseResponse(
            success=True,
            message="Ticket updated successfully",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/tickets/{ticket_id}",
    response_model=BaseResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a ticket",
    description="Deletes a ticket permanently from the repository."
)
async def delete_ticket(
    ticket_id: str = Path(..., description="The ID of the ticket to delete"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        success = await service.delete_ticket(ticket_id)
        return BaseResponse(
            success=True,
            message="Ticket deleted successfully",
            data=success
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post(
    "/tickets/{ticket_id}/status",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_200_OK,
    summary="Update ticket status",
    description="Updates the status (open, in_progress, closed, escalated) of a ticket and logs a timeline event."
)
async def update_status(
    payload: TicketStatusUpdate,
    ticket_id: str = Path(..., description="The ID of the ticket to transition"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.update_status(ticket_id, payload, actor="agent")
        return BaseResponse(
            success=True,
            message="Ticket status updated",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/tickets/{ticket_id}/priority",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_200_OK,
    summary="Update ticket priority",
    description="Updates the priority (low, medium, high, urgent) of a ticket and logs a timeline event."
)
async def update_priority(
    payload: TicketPriorityUpdate,
    ticket_id: str = Path(..., description="The ID of the ticket to update"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.update_priority(ticket_id, payload, actor="agent")
        return BaseResponse(
            success=True,
            message="Ticket priority updated",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/tickets/{ticket_id}/assign",
    response_model=BaseResponse[Ticket],
    status_code=status.HTTP_200_OK,
    summary="Assign agent to ticket",
    description="Assigns or reassigns an agent to work on the support ticket."
)
async def assign_agent(
    payload: TicketAgentAssign,
    ticket_id: str = Path(..., description="The ID of the ticket to assign"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        ticket = await service.assign_agent(ticket_id, payload, actor="admin")
        return BaseResponse(
            success=True,
            message="Agent assigned successfully",
            data=ticket
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=BaseResponse[TicketComment],
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to ticket",
    description="Appends a new internal or public comment from an agent or customer to the ticket's thread."
)
async def add_comment(
    payload: TicketCommentCreate,
    ticket_id: str = Path(..., description="The ID of the ticket to comment on"),
    service: TicketService = Depends(get_ticket_service)
):
    try:
        comment = await service.add_comment(ticket_id, payload)
        return BaseResponse(
            success=True,
            message="Comment added successfully",
            data=comment
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
