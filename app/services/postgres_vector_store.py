from typing import Any

from app.database.database import SessionLocal
from app.db_models.ai_knowledge_base import (
    AIKnowledgeBase as DBAIKnowledgeBase,
)
from app.schemas.chunk import Chunk

# Import at module level is now safe because vector_store.py uses lazy imports
from app.services.vector_store import VectorStore


class PostgresVectorStore(VectorStore):
    def __init__(self):
        self.db = SessionLocal()

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """
        Embeddings are already stored in the ai_knowledge_base table,
        so nothing needs to be done here.
        """
        return

    def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 4,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        query = self.db.query(DBAIKnowledgeBase).filter(
            DBAIKnowledgeBase.is_active.is_(True)
        )

        if filters:
            for key, value in filters.items():
                if (
                    value is not None
                    and hasattr(DBAIKnowledgeBase, key)
                ):
                    query = query.filter(
                        getattr(DBAIKnowledgeBase, key) == value
                    )

        rows = (
            query.order_by(
                DBAIKnowledgeBase.embedding.cosine_distance(
                    query_vector
                )
            )
            .limit(top_k)
            .all()
        )

        results = []

        for row in rows:
            chunk = Chunk(
                id=str(row.id),
                document_id=str(row.id),
                content=row.content,
                embedding=row.embedding,
                metadata={
                    "title": row.document_title,
                    "document_type": row.document_type,
                    "source": row.source,
                },
            )

            results.append(
                {
                    "chunk": chunk,
                    "score": 1.0,
                }
            )

        return results

    def delete_document(self, document_id: str) -> None:
        return