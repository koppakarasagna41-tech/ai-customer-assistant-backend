from datetime import UTC, datetime

from app.models.ai_priority_prediction import (
    AIPriorityPrediction,
)
from app.repositories.ai_priority_prediction_repository import (
    AIPriorityPredictionRepository,
    get_ai_priority_prediction_repository,
)
from app.schemas.ai_priority_prediction import (
    AIPriorityPredictionCreate,
    AIPriorityPredictionUpdate,
)


class AIPriorityPredictionService:
    def __init__(
        self,
        repository: AIPriorityPredictionRepository | None = None,
    ):
        self.repository = repository if repository else get_ai_priority_prediction_repository()

    async def create_prediction(
        self,
        data: AIPriorityPredictionCreate,
    ) -> AIPriorityPrediction:
        prediction = AIPriorityPrediction(
            id=0,
            ticket_id=data.ticket_id,
            predicted_priority=data.predicted_priority,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            raw_response=data.raw_response,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(prediction)

    async def get_prediction(
        self,
        ticket_id: str,
    ) -> AIPriorityPrediction | None:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_prediction(
        self,
        ticket_id: str,
        data: AIPriorityPredictionUpdate,
    ) -> AIPriorityPrediction | None:
        return await self.repository.update(
            ticket_id,
            predicted_priority=data.predicted_priority,
            confidence_score=data.confidence_score,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            raw_response=data.raw_response,
        )

    async def delete_prediction(
        self,
        ticket_id: str,
    ) -> bool:
        return await self.repository.delete(ticket_id)


def get_ai_priority_prediction_service() -> AIPriorityPredictionService:
    return AIPriorityPredictionService()
