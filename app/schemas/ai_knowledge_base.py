from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIKnowledgeBaseCreate(BaseModel):
    document_title: str
    document_type: str
    content: str
    source: str | None = None
    embedding_model: str | None = None
    chunk_id: str | None = None
    is_active: bool = True


class AIKnowledgeBaseUpdate(BaseModel):
    document_title: str | None = None
    document_type: str | None = None
    content: str | None = None
    source: str | None = None
    embedding_model: str | None = None
    chunk_id: str | None = None
    is_active: bool | None = None


class AIKnowledgeBaseResponse(BaseModel):
    id: int
    document_title: str
    document_type: str
    content: str
    source: str | None = None
    embedding_model: str | None = None
    chunk_id: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)