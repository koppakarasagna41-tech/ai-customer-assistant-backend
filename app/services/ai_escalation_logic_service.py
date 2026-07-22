from datetime import UTC, datetime

from app.models.ai_escalation_logic import (
    AIEscalationLogic,
)
from app.repositories.ai_escalation_logic_repository import (
    AIEscalationLogicRepository,
    get_ai_escalation_logic_repository,
)
from app.schemas.ai_escalation_logic import (
    AIEscalationLogicCreate,
    AIEscalationLogicUpdate,
)


class AIEscalationLogicService:
    def __init__(
        self,
        repository: AIEscalationLogicRepository | None = None,
    ):
        self.repository = repository if repository else get_ai_escalation_logic_repository()

    async def create_escalation(
        self,
        data: AIEscalationLogicCreate,
    ) -> AIEscalationLogic:
        escalation = AIEscalationLogic(
            id=0,
            ticket_id=data.ticket_id,
            escalation_reason=data.escalation_reason,
            escalation_level=data.escalation_level,
            assigned_team=data.assigned_team,
            status=data.status,
            auto_escalated=data.auto_escalated,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(escalation)

    async def get_escalations(
        self,
        ticket_id: str,
    ) -> list[AIEscalationLogic]:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_escalation(
        self,
        escalation_id: int,
        data: AIEscalationLogicUpdate,
    ) -> AIEscalationLogic | None:
        return await self.repository.update(
            escalation_id,
            escalation_reason=data.escalation_reason,
            escalation_level=data.escalation_level,
            assigned_team=data.assigned_team,
            status=data.status,
            auto_escalated=data.auto_escalated,
        )

    async def delete_escalation(
        self,
        escalation_id: int,
    ) -> bool:
        return await self.repository.delete(escalation_id)


def get_ai_escalation_logic_service() -> AIEscalationLogicService:
    return AIEscalationLogicService()
