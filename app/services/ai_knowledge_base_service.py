from datetime import UTC, datetime

from app.models.ai_knowledge_base import AIKnowledgeBase
from app.repositories.ai_knowledge_base_repository import (
    AIKnowledgeBaseRepository,
    get_ai_knowledge_base_repository,
)
from app.schemas.ai_knowledge_base import (
    AIKnowledgeBaseCreate,
    AIKnowledgeBaseUpdate,
)
from app.services.embedding_service import EmbeddingService


class AIKnowledgeBaseService:
    def __init__(
        self,
        repository: AIKnowledgeBaseRepository | None = None,
    ):
        self.repository = repository if repository else get_ai_knowledge_base_repository()
        self.embedding_service = EmbeddingService()

    async def create_knowledge(
        self,
        data: AIKnowledgeBaseCreate,
    ) -> AIKnowledgeBase:
        self.embedding_service.embed_text(data.content)

        knowledge = AIKnowledgeBase(
            id=0,
            document_title=data.document_title,
            document_type=data.document_type,
            content=data.content,
            source=data.source,
            embedding_model=data.embedding_model,
            chunk_id=data.chunk_id,
            is_active=data.is_active,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(knowledge)

    async def get_knowledge(
        self,
        knowledge_id: int,
    ) -> AIKnowledgeBase | None:
        return await self.repository.get_by_id(knowledge_id)

    async def get_all_knowledge(
        self,
    ) -> list[AIKnowledgeBase]:
        return await self.repository.get_all()

    async def update_knowledge(
        self,
        knowledge_id: int,
        data: AIKnowledgeBaseUpdate,
    ) -> AIKnowledgeBase | None:
        return await self.repository.update(
            knowledge_id,
            document_title=data.document_title,
            document_type=data.document_type,
            content=data.content,
            source=data.source,
            embedding_model=data.embedding_model,
            chunk_id=data.chunk_id,
            is_active=data.is_active,
        )

    async def delete_knowledge(
        self,
        knowledge_id: int,
    ) -> bool:
        return await self.repository.delete(knowledge_id)


def get_ai_knowledge_base_service() -> AIKnowledgeBaseService:
    return AIKnowledgeBaseService()
