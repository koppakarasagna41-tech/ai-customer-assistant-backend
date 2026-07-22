from datetime import UTC, datetime

from app.models.ai_ticket_classification import (
    AITicketClassification,
)
from app.repositories.ai_ticket_classification_repository import (
    AITicketClassificationRepository,
    get_ai_ticket_classification_repository,
)
from app.schemas.ai_ticket_classification import (
    AITicketClassificationCreate,
    AITicketClassificationUpdate,
)


class AITicketClassificationService:
    def __init__(
        self,
        repository: AITicketClassificationRepository | None = None,
    ):
        self.repository = (
            repository
            if repository
            else get_ai_ticket_classification_repository()
        )

    async def create_classification(
        self,
        data: AITicketClassificationCreate,
    ) -> AITicketClassification:
        classification = AITicketClassification(
            id=0,
            ticket_id=data.ticket_id,
            predicted_category=data.predicted_category,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            raw_response=data.raw_response,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(classification)

    async def get_classification(
        self,
        ticket_id: str,
    ) -> AITicketClassification | None:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_classification(
        self,
        ticket_id: str,
        data: AITicketClassificationUpdate,
    ) -> AITicketClassification | None:
        return await self.repository.update(
            ticket_id,
            predicted_category=data.predicted_category,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            raw_response=data.raw_response,
        )

    async def delete_classification(
        self,
        ticket_id: str,
    ) -> bool:
        return await self.repository.delete(ticket_id)


def get_ai_ticket_classification_service() -> (
    AITicketClassificationService
):
    return AITicketClassificationService()