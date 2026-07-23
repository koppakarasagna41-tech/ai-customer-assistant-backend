from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_knowledge_base import (
    AIKnowledgeBase as DBAIKnowledgeBase,
)
from app.models.ai_knowledge_base import (
    AIKnowledgeBase,
)


class AIKnowledgeBaseRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(
        self,
        knowledge: AIKnowledgeBase,
    ) -> AIKnowledgeBase:
        db_knowledge = DBAIKnowledgeBase(
            document_title=knowledge.document_title,
            document_type=knowledge.document_type,
            content=knowledge.content,
            source=knowledge.source,
            embedding_model=knowledge.embedding_model,
            embedding=knowledge.embedding,
            chunk_id=knowledge.chunk_id,
            is_active=knowledge.is_active,
        )

        self.db.add(db_knowledge)
        self.db.commit()
        self.db.refresh(db_knowledge)

        return AIKnowledgeBase.model_validate(db_knowledge)

    async def get_by_id(
        self,
        knowledge_id: int,
    ) -> AIKnowledgeBase | None:
        knowledge = (
            self.db.query(DBAIKnowledgeBase).filter(DBAIKnowledgeBase.id == knowledge_id).first()
        )

        if not knowledge:
            return None

        return AIKnowledgeBase.model_validate(knowledge)

    async def get_all(
        self,
    ) -> list[AIKnowledgeBase]:
        knowledge = self.db.query(DBAIKnowledgeBase).order_by(DBAIKnowledgeBase.id.desc()).all()

        return [AIKnowledgeBase.model_validate(item) for item in knowledge]

    async def update(
        self,
        knowledge_id: int,
        **kwargs,
    ) -> AIKnowledgeBase | None:
        knowledge = (
            self.db.query(DBAIKnowledgeBase).filter(DBAIKnowledgeBase.id == knowledge_id).first()
        )

        if not knowledge:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(knowledge, key, value)

        self.db.commit()
        self.db.refresh(knowledge)

        return AIKnowledgeBase.model_validate(knowledge)

    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[AIKnowledgeBase]:
        knowledge = (
            self.db.query(DBAIKnowledgeBase)
            .filter(DBAIKnowledgeBase.is_active.is_(True))
            .order_by(DBAIKnowledgeBase.embedding.cosine_distance(embedding))
            .limit(limit)
            .all()
        )

        return [AIKnowledgeBase.model_validate(item) for item in knowledge]

    async def delete(
        self,
        knowledge_id: int,
    ) -> bool:
        knowledge = (
            self.db.query(DBAIKnowledgeBase).filter(DBAIKnowledgeBase.id == knowledge_id).first()
        )

        if not knowledge:
            return False

        self.db.delete(knowledge)
        self.db.commit()

        return True


def get_ai_knowledge_base_repository() -> AIKnowledgeBaseRepository:
    return AIKnowledgeBaseRepository()
