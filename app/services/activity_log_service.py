from datetime import UTC, datetime

from app.models.activity_log import ActivityLog
from app.repositories.activity_log_repository import (
    ActivityLogRepository,
    get_activity_log_repository,
)
from app.schemas.activity_log import ActivityLogCreate


class ActivityLogService:
    def __init__(
        self,
        repository: ActivityLogRepository | None = None,
    ):
        self.repository = repository if repository else get_activity_log_repository()

    async def create_activity_log(
        self,
        data: ActivityLogCreate,
    ) -> ActivityLog:
        activity_log = ActivityLog(
            id=0,
            ticket_id=data.ticket_id,
            action=data.action,
            performed_by=data.performed_by,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(activity_log)

    async def get_activity_logs(
        self,
        ticket_id: str,
    ) -> list[ActivityLog]:
        return await self.repository.list_by_ticket(ticket_id)

    async def get_activity_log(
        self,
        activity_log_id: int,
    ) -> ActivityLog | None:
        return await self.repository.get_by_id(activity_log_id)

    async def delete_activity_log(
        self,
        activity_log_id: int,
    ) -> bool:
        return await self.repository.delete(activity_log_id)


def get_activity_log_service() -> ActivityLogService:
    return ActivityLogService()
