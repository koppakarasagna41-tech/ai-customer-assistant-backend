import logging

from app.schemas.retrieval import RetrievalFilter, RetrievalResponse, RetrievedChunk
from app.services.embedding_service import get_embedding_service
from app.services.metadata_filter import get_metadata_filter_builder
from app.services.query_classifier import get_query_classifier
from app.services.query_rewriter import get_query_rewriter
from app.services.reranker import get_reranker
from app.services.retrieval_cache import get_retrieval_cache
from app.services.vector_store import get_vector_store

logger = logging.getLogger("app.services.retriever")


class DocumentRetriever:
    """
    Orchestrates the entire Stage 1 RAG Retrieval Pipeline:
    Query -> Local Clean -> Semantic Rewrite -> Classification -> Vector
    Similarity -> Rerank -> Cache -> Output
    """

    def __init__(self):
        self.rewriter = get_query_rewriter()
        self.classifier = get_query_classifier()
        self.filter_builder = get_metadata_filter_builder()
        self.cache = get_retrieval_cache()
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.reranker = get_reranker()

    async def retrieve(
        self,
        query: str,
        top_k: int = 4,
        filters: RetrievalFilter | None = None,
        use_cache: bool = True,
    ) -> RetrievalResponse:
        logger.info(f"Initiating document retrieval pipeline for query: '{query[:40]}...'")

        # 1. Classify query (intent, categories, extracted entities)
        classification_data = self.classifier.classify_query(query)
        category = classification_data.get("category", "general")

        # 2. Build metadata filter dictionary
        metadata_filters = self.filter_builder.build_filters(filters, classification_data)

        # 3. Check Cache
        if use_cache:
            cached_results = self.cache.get(query, metadata_filters)
            if cached_results is not None:
                return RetrievalResponse(
                    query=query,
                    rewritten_query=query,  # cached
                    classification=category,
                    chunks=cached_results,
                    from_cache=True,
                )

        # 4. Rewrite query semantically for vector search (Stage 1 query expansion)
        rewritten_query = await self.rewriter.rewrite(query)

        # 5. Generate query embedding
        query_vector = self.embedding_service.embed_text(rewritten_query)

        # 6. Retrieve top candidates from vector store (retrieve double top_k for reranking)
        retrieval_limit = max(top_k * 2, 8)
        search_results = self.vector_store.similarity_search(
            query_vector=query_vector, top_k=retrieval_limit, filters=metadata_filters
        )

        # Format candidates as RetrievedChunks
        candidates = []
        for res in search_results:
            chunk = res["chunk"]
            score = res["score"]
            candidates.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=score,
                    metadata=chunk.metadata,
                )
            )

        # 7. Rerank candidates semantically using semantic+lexical hybrid scorer
        reranked_chunks = self.reranker.rerank(query=query, candidates=candidates, top_n=top_k)

        # 8. Store in cache
        if use_cache and reranked_chunks:
            self.cache.set(query, reranked_chunks, metadata_filters)

        return RetrievalResponse(
            query=query,
            rewritten_query=rewritten_query,
            classification=category,
            chunks=reranked_chunks,
            from_cache=False,
        )


def get_retriever() -> DocumentRetriever:
    return DocumentRetriever()
