from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notification_service import (
    NotificationService,
    get_notification_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    notification: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.create_notification(notification)


@router.get(
    "/{user_id}",
    response_model=list[NotificationResponse],
)
async def get_notifications(
    user_id: str,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_notifications(user_id)


@router.get(
    "/details/{notification_id}",
    response_model=NotificationResponse,
)
async def get_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.get_notification(notification_id)

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_as_read(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.mark_as_read(notification_id)

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.delete(
    "/{notification_id}",
)
async def delete_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    deleted = await service.delete_notification(notification_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return {
        "success": True,
        "message": "Notification deleted successfully",
    }