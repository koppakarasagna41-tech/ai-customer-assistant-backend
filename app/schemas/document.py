from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    title: Optional[str] = Field(None, description="Title of the document")
    source: Optional[str] = Field(None, description="Source file path or URL")
    author: Optional[str] = Field(None, description="Author of the document")
    category: Optional[str] = Field(None, description="Category (e.g., policy, support, faq)")
    product: Optional[str] = Field(None, description="Product associated with the document")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Any other custom metadata keys")

class Document(BaseModel):
    id: str = Field(..., description="Unique document identifier")
    content: str = Field(..., description="Raw text content of the document")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    mime_type: str = Field("text/plain", description="MIME type of the source file")
    chunk_count: int = Field(0, description="Number of generated chunks")
