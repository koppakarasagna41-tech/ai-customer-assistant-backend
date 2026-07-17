from typing import Any

from pydantic import BaseModel, Field


class RetrievalFilter(BaseModel):
    category: str | None = Field(None, description="Filter by category")
    product: str | None = Field(None, description="Filter by product name")
    custom_filters: dict[str, Any] = Field(
        default_factory=dict, description="Additional exact match filter keys"
    )


class RetrievalRequest(BaseModel):
    query: str = Field(..., description="The user question or search query")
    top_k: int | None = Field(4, description="Number of results to retrieve before reranking")
    filter: RetrievalFilter | None = Field(None, description="Metadata filtering criteria")
    session_id: str | None = Field(None, description="Session ID for search history/caching")


class RetrievedChunk(BaseModel):
    chunk_id: str = Field(..., description="ID of retrieved chunk")
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="The chunk content text")
    score: float = Field(..., description="Similarity score (retrieval or reranked)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class RetrievalResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    rewritten_query: str | None = Field(None, description="Rewritten/expanded query")
    classification: str | None = Field(None, description="Detected category/intent of query")
    chunks: list[RetrievedChunk] = Field(..., description="List of matched document chunks")
    from_cache: bool = Field(False, description="Whether the response was served from cache")
