from datetime import UTC, datetime

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import (
    AuditLogRepository,
    get_audit_log_repository,
)
from app.schemas.audit_log import AuditLogCreate


class AuditLogService:
    def __init__(
        self,
        repository: AuditLogRepository | None = None,
    ):
        self.repository = repository if repository else get_audit_log_repository()

    async def create_audit_log(
        self,
        data: AuditLogCreate,
    ) -> AuditLog:
        audit_log = AuditLog(
            id=0,
            entity=data.entity,
            entity_id=data.entity_id,
            action=data.action,
            performed_by=data.performed_by,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(audit_log)

    async def get_audit_logs(
        self,
    ) -> list[AuditLog]:
        return await self.repository.list_all()

    async def get_audit_log(
        self,
        audit_log_id: int,
    ) -> AuditLog | None:
        return await self.repository.get_by_id(audit_log_id)

    async def delete_audit_log(
        self,
        audit_log_id: int,
    ) -> bool:
        return await self.repository.delete(audit_log_id)


def get_audit_log_service() -> AuditLogService:
    return AuditLogService()
