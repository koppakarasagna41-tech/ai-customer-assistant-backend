from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Citation(BaseModel):
    id: str = Field(..., description="Unique citation identifier (e.g., [1], [2])")
    document_id: str = Field(..., description="ID of the cited document")
    title: str = Field(..., description="Title or source name of the cited document")
    snippet: str = Field(..., description="Relevant snippet text cited")
    chunk_id: str = Field(..., description="Specific chunk cited")

class RAGResponse(BaseModel):
    answer: str = Field(..., description="The generated response from the RAG pipeline using retrieved context")
    citations: List[Citation] = Field(default_factory=list, description="Citations referenced in the generated answer")
    relevance_score: float = Field(..., description="Overall confidence/relevance score of retrieved knowledge")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata (token usage, pipeline times)")
