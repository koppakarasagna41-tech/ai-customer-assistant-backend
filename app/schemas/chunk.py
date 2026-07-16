from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class Chunk(BaseModel):
    id: str = Field(..., description="Unique chunk ID (e.g., doc_id_chunk_index)")
    document_id: str = Field(..., description="ID of the parent document")
    index: int = Field(..., description="0-indexed position of this chunk in the document")
    content: str = Field(..., description="The chunk text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Enriched metadata including product, category, custom tags")
    embedding: Optional[List[float]] = Field(None, description="The vector embedding of the chunk text")
