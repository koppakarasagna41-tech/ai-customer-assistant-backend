from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse,
)
from app.services.activity_log_service import (
    ActivityLogService,
    get_activity_log_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ActivityLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity_log(
    activity_log: ActivityLogCreate,
    service: ActivityLogService = Depends(
        get_activity_log_service,
    ),
):
    return await service.create_activity_log(activity_log)


@router.get(
    "/{ticket_id}",
    response_model=list[ActivityLogResponse],
)
async def get_activity_logs(
    ticket_id: str,
    service: ActivityLogService = Depends(
        get_activity_log_service,
    ),
):
    return await service.get_activity_logs(ticket_id)


@router.get(
    "/details/{activity_log_id}",
    response_model=ActivityLogResponse,
)
async def get_activity_log(
    activity_log_id: int,
    service: ActivityLogService = Depends(
        get_activity_log_service,
    ),
):
    activity_log = await service.get_activity_log(activity_log_id)

    if activity_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found",
        )

    return activity_log


@router.delete(
    "/{activity_log_id}",
)
async def delete_activity_log(
    activity_log_id: int,
    service: ActivityLogService = Depends(
        get_activity_log_service,
    ),
):
    deleted = await service.delete_activity_log(activity_log_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found",
        )

    return {
        "success": True,
        "message": "Activity log deleted successfully",
    }
