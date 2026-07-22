from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.assignment_history import (
    AssignmentHistoryCreate,
    AssignmentHistoryResponse,
)
from app.services.assignment_history_service import (
    AssignmentHistoryService,
    get_assignment_history_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AssignmentHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    assignment: AssignmentHistoryCreate,
    service: AssignmentHistoryService = Depends(
        get_assignment_history_service
    ),
):
    return await service.create_assignment(assignment)


@router.get(
    "/{ticket_id}",
    response_model=list[AssignmentHistoryResponse],
)
async def get_assignments(
    ticket_id: str,
    service: AssignmentHistoryService = Depends(
        get_assignment_history_service
    ),
):
    return await service.get_assignments(ticket_id)


@router.get(
    "/details/{assignment_id}",
    response_model=AssignmentHistoryResponse,
)
async def get_assignment(
    assignment_id: int,
    service: AssignmentHistoryService = Depends(
        get_assignment_history_service
    ),
):
    assignment = await service.get_assignment(assignment_id)

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment history not found",
        )

    return assignment


@router.delete(
    "/{assignment_id}",
)
async def delete_assignment(
    assignment_id: int,
    service: AssignmentHistoryService = Depends(
        get_assignment_history_service
    ),
):
    deleted = await service.delete_assignment(assignment_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment history not found",
        )

    return {
        "success": True,
        "message": "Assignment history deleted successfully",
    }