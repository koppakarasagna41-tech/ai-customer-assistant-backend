from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String, Text

from app.database.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    session_id = Column(String, primary_key=True, index=True)

    user_id = Column(String)

    summary = Column(Text)

    messages = Column(JSON)

    session_metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
