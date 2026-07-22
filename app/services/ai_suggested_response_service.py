from datetime import UTC, datetime

from app.models.ai_suggested_response import (
    AISuggestedResponse,
)
from app.repositories.ai_suggested_response_repository import (
    AISuggestedResponseRepository,
    get_ai_suggested_response_repository,
)
from app.schemas.ai_suggested_response import (
    AISuggestedResponseCreate,
    AISuggestedResponseUpdate,
)


class AISuggestedResponseService:
    def __init__(
        self,
        repository: AISuggestedResponseRepository | None = None,
    ):
        self.repository = (
            repository
            if repository
            else get_ai_suggested_response_repository()
        )

    async def create_response(
        self,
        data: AISuggestedResponseCreate,
    ) -> AISuggestedResponse:
        response = AISuggestedResponse(
            id=0,
            ticket_id=data.ticket_id,
            suggested_response=data.suggested_response,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            status=data.status,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(response)

    async def get_response(
        self,
        ticket_id: str,
    ) -> AISuggestedResponse | None:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_response(
        self,
        ticket_id: str,
        data: AISuggestedResponseUpdate,
    ) -> AISuggestedResponse | None:
        return await self.repository.update(
            ticket_id,
            suggested_response=data.suggested_response,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            status=data.status,
        )

    async def delete_response(
        self,
        ticket_id: str,
    ) -> bool:
        return await self.repository.delete(ticket_id)


def get_ai_suggested_response_service() -> (
    AISuggestedResponseService
):
    return AISuggestedResponseService()