from app.models.notification import Notification
from app.repositories.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from app.schemas.notification import (
    NotificationCreate,
)


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository | None = None,
    ):
        self.repository = repository if repository else get_notification_repository()

    async def create_notification(
        self,
        data: NotificationCreate,
    ) -> Notification:
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            type=data.type,
        )

        return await self.repository.create(notification)

    async def get_notifications(
        self,
        user_id: str,
    ) -> list[Notification]:
        return await self.repository.list_by_user(user_id)

    async def get_notification(
        self,
        notification_id: int,
    ) -> Notification | None:
        return await self.repository.get_by_id(notification_id)

    async def mark_as_read(
        self,
        notification_id: int,
    ) -> Notification | None:
        return await self.repository.mark_as_read(notification_id)

    async def delete_notification(
        self,
        notification_id: int,
    ) -> bool:
        return await self.repository.delete(notification_id)


def get_notification_service() -> NotificationService:
    return NotificationService()
