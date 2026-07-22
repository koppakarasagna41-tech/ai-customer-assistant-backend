from datetime import UTC, datetime

from app.models.assignment_history import AssignmentHistory
from app.repositories.assignment_history_repository import (
    AssignmentHistoryRepository,
    get_assignment_history_repository,
)
from app.schemas.assignment_history import (
    AssignmentHistoryCreate,
)


class AssignmentHistoryService:
    def __init__(
        self,
        repository: AssignmentHistoryRepository | None = None,
    ):
        self.repository = repository if repository else get_assignment_history_repository()

    async def create_assignment(
        self,
        data: AssignmentHistoryCreate,
    ) -> AssignmentHistory:
        assignment = AssignmentHistory(
            id=0,
            ticket_id=data.ticket_id,
            agent_id=data.agent_id,
            assigned_at=datetime.now(UTC),
        )

        return await self.repository.create(assignment)

    async def get_assignments(
        self,
        ticket_id: str,
    ) -> list[AssignmentHistory]:
        return await self.repository.list_by_ticket(ticket_id)

    async def get_assignment(
        self,
        assignment_id: int,
    ) -> AssignmentHistory | None:
        return await self.repository.get_by_id(assignment_id)

    async def delete_assignment(
        self,
        assignment_id: int,
    ) -> bool:
        return await self.repository.delete(assignment_id)


def get_assignment_history_service() -> AssignmentHistoryService:
    return AssignmentHistoryService()
