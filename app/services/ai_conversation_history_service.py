from datetime import UTC, datetime

from app.models.ai_conversation_history import (
    AIConversationHistory,
)
from app.repositories.ai_conversation_history_repository import (
    AIConversationHistoryRepository,
    get_ai_conversation_history_repository,
)
from app.schemas.ai_conversation_history import (
    AIConversationHistoryCreate,
    AIConversationHistoryUpdate,
)


class AIConversationHistoryService:
    def __init__(
        self,
        repository: AIConversationHistoryRepository | None = None,
    ):
        self.repository = repository if repository else get_ai_conversation_history_repository()

    async def create_conversation(
        self,
        data: AIConversationHistoryCreate,
    ) -> AIConversationHistory:
        conversation = AIConversationHistory(
            id=0,
            ticket_id=data.ticket_id,
            user_message=data.user_message,
            ai_response=data.ai_response,
            model_name=data.model_name,
            conversation_id=data.conversation_id,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(conversation)

    async def get_conversations(
        self,
        ticket_id: str,
    ) -> list[AIConversationHistory]:
        return await self.repository.get_by_ticket_id(ticket_id)

    async def update_conversation(
        self,
        conversation_id: int,
        data: AIConversationHistoryUpdate,
    ) -> AIConversationHistory | None:
        return await self.repository.update(
            conversation_id,
            user_message=data.user_message,
            ai_response=data.ai_response,
            model_name=data.model_name,
            conversation_id=data.conversation_id,
        )

    async def delete_conversation(
        self,
        conversation_id: int,
    ) -> bool:
        return await self.repository.delete(conversation_id)


def get_ai_conversation_history_service() -> AIConversationHistoryService:
    return AIConversationHistoryService()
