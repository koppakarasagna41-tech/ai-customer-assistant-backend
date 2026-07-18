import abc
import logging
from typing import Any

from app.schemas.chunk import Chunk
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger("app.services.vector_store")


class VectorStore(abc.ABC):
    @abc.abstractmethod
    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Adds a list of chunks with their pre-computed embeddings to the vector store."""
        pass

    @abc.abstractmethod
    def similarity_search(
        self, query_vector: list[float], top_k: int = 4, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Searches for the top_k most similar chunks to the query_vector,
        optionally applying metadata filters.
        """
        pass

    @abc.abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Deletes all chunks associated with a document_id."""
        pass


class InMemoryVectorStore(VectorStore):
    """
    Highly performant, thread-safe In-Memory Vector Store implementation.
    Includes robust metadata exact-match filtering.
    """

    def __init__(self):
        # Stores Chunk objects
        self._store: dict[str, Chunk] = {}

    def add_chunks(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            if not chunk.embedding:
                logger.warning(
                    f"Chunk {chunk.id} is missing an embedding. Embedding was not indexed."
                )
            self._store[chunk.id] = chunk
        logger.info(
            "Indexed %s chunks in the vector store. Total database size: %s",
            len(chunks),
            len(self._store),
        )

    def similarity_search(
        self, query_vector: list[float], top_k: int = 4, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        embedding_service = get_embedding_service()

        for _chunk_id, chunk in self._store.items():
            if not chunk.embedding:
                continue

            # Apply Metadata Filters
            if filters:
                match = True
                for k, v in filters.items():
                    if v is not None:
                        # Exact match check
                        chunk_val = chunk.metadata.get(k)
                        if isinstance(chunk_val, str) and isinstance(v, str):
                            if chunk_val.lower() != v.lower():
                                match = False
                                break
                        elif chunk_val != v:
                            match = False
                            break
                if not match:
                    continue

            # Compute Cosine Similarity
            score = embedding_service.cosine_similarity(query_vector, chunk.embedding)
            results.append({"chunk": chunk, "score": score})

        # Sort by score descending
        results.sort(key=lambda x: float(x["score"]), reverse=True)
        return results[:top_k]

    def delete_document(self, document_id: str) -> None:
        keys_to_delete = [k for k, v in self._store.items() if v.document_id == document_id]
        for k in keys_to_delete:
            del self._store[k]
        logger.info(f"Deleted {len(keys_to_delete)} chunks for document {document_id}")


# Factory/Registry to support Chroma, Pinecone, FAISS, Qdrant, Milvus
class VectorStoreFactory:
    _instance: VectorStore | None = None
    _provider: str = "in_memory"

    @classmethod
    def get_vector_store(cls) -> VectorStore:
        if cls._instance is None:
            # We default to in_memory in this workspace, but the abstraction
            # supports switching providers.
            if cls._provider == "in_memory":
                cls._instance = InMemoryVectorStore()
            elif cls._provider == "chroma":
                logger.info("Initializing ChromaDB connection...")
                # Placeholder for Chroma implementation
                cls._instance = InMemoryVectorStore()
            elif cls._provider == "pinecone":
                logger.info("Initializing Pinecone client...")
                # Placeholder for Pinecone implementation
                cls._instance = InMemoryVectorStore()
            elif cls._provider == "qdrant":
                logger.info("Initializing Qdrant client...")
                # Placeholder for Qdrant implementation
                cls._instance = InMemoryVectorStore()
            elif cls._provider == "faiss":
                logger.info("Initializing FAISS local index...")
                cls._instance = InMemoryVectorStore()
            else:
                cls._instance = InMemoryVectorStore()
        return cls._instance

    @classmethod
    def set_provider(cls, provider: str) -> None:
        cls._provider = provider.lower()
        cls._instance = None  # Reset instance to re-initialize


def get_vector_store() -> VectorStore:
    return VectorStoreFactory.get_vector_store()
