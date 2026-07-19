from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str | None = Field(None, description="Title of the document")
    source: str | None = Field(None, description="Source file path or URL")
    author: str | None = Field(None, description="Author of the document")
    category: str | None = Field(None, description="Category (e.g., policy, support, faq)")
    product: str | None = Field(None, description="Product associated with the document")
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    custom_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Any other custom metadata keys",
    )


class Document(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Raw text content")
    metadata: DocumentMetadata = Field(
        default_factory=lambda: DocumentMetadata(
            title=None,
            source=None,
            author=None,
            category=None,
            product=None,
        )
    )
    mime_type: str = Field("text/plain", description="MIME type")
    chunk_count: int = Field(0, description="Number of generated chunks")
