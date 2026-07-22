from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from pgvector.sqlalchemy import Vector

from app.database.database import Base


class AIKnowledgeBase(Base):
    __tablename__ = "ai_knowledge_base"

    id = Column(Integer, primary_key=True, index=True)

    document_title = Column(
        String,
        nullable=False,
    )

    document_type = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    source = Column(
        String,
        nullable=True,
    )

    embedding_model = Column(
        String,
        nullable=True,
    )
    embedding = Column(
    Vector(768),
    nullable=True,
)

    chunk_id = Column(
        String,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )