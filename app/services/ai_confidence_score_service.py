from datetime import UTC, datetime

from app.models.ai_confidence_score import (
    AIConfidenceScore,
)
from app.repositories.ai_confidence_score_repository import (
    AIConfidenceScoreRepository,
    get_ai_confidence_score_repository,
)
from app.schemas.ai_confidence_score import (
    AIConfidenceScoreCreate,
    AIConfidenceScoreUpdate,
)


class AIConfidenceScoreService:
    def __init__(
        self,
        repository: AIConfidenceScoreRepository | None = None,
    ):
        self.repository = repository if repository else get_ai_confidence_score_repository()

    async def create_confidence_score(
        self,
        data: AIConfidenceScoreCreate,
    ) -> AIConfidenceScore:
        confidence = AIConfidenceScore(
            id=0,
            ticket_id=data.ticket_id,
            confidence_score=data.confidence_score,
            prediction_type=data.prediction_type,
            model_name=data.model_name,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(confidence)

    async def get_confidence_scores(
        self,
        ticket_id: str,
    ) -> list[AIConfidenceScore]:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_confidence_score(
        self,
        confidence_id: int,
        data: AIConfidenceScoreUpdate,
    ) -> AIConfidenceScore | None:
        return await self.repository.update(
            confidence_id,
            confidence_score=data.confidence_score,
            prediction_type=data.prediction_type,
            model_name=data.model_name,
        )

    async def delete_confidence_score(
        self,
        confidence_id: int,
    ) -> bool:
        return await self.repository.delete(confidence_id)


def get_ai_confidence_score_service() -> AIConfidenceScoreService:
    return AIConfidenceScoreService()
