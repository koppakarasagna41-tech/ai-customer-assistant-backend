from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIKnowledgeBase(BaseModel):
    id: int
    document_title: str
    document_type: str
    content: str
    source: str | None = None
    embedding_model: str | None = None
    embedding: list[float] | None = None
    chunk_id: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
