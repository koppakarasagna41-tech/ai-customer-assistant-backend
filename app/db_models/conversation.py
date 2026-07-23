from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String, Text, func

from app.database.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    session_id = Column(String, primary_key=True, index=True)

    user_id = Column(String, nullable=True)

    summary = Column(Text, nullable=True)

    messages = Column(JSON, nullable=True, default=list)

    session_metadata = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)
