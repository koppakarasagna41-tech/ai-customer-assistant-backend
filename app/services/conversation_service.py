from app.models.conversation import Conversation
from app.repositories.conversation_repository import (
    ConversationRepository,
    get_conversation_repository,
)
from app.schemas.conversation import ConversationState


class ConversationService:
    def __init__(self, repository: ConversationRepository | None = None):
        self.repository = repository if repository else get_conversation_repository()

    async def create_conversation(self, data: ConversationState) -> Conversation:
        conversation = Conversation(
            session_id=data.session_id,
            user_id=data.user_id,
            summary=data.summary,
            messages=[message.model_dump(mode="json") for message in data.messages],
            session_metadata=data.metadata,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )
        return await self.repository.create(conversation)

    async def get_conversation(self, session_id: str) -> Conversation | None:
        return await self.repository.get_by_id(session_id)

    async def list_user_conversations(self, user_id: str) -> list[Conversation]:
        return await self.repository.list_by_user(user_id)

    async def update_conversation(self, data: ConversationState) -> Conversation:
        conversation = Conversation(
            session_id=data.session_id,
            user_id=data.user_id,
            summary=data.summary,
            messages=[message.model_dump(mode="json") for message in data.messages],
            session_metadata=data.metadata,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )
        return await self.repository.update(conversation)

    async def delete_conversation(self, session_id: str) -> bool:
        return await self.repository.delete(session_id)


def get_conversation_service() -> ConversationService:
    return ConversationService()
