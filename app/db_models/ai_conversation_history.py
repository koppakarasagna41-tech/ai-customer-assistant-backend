from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database.database import Base


class AIConversationHistory(Base):
    __tablename__ = "ai_conversation_history"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        String,
        nullable=False,
    )

    user_message = Column(
        Text,
        nullable=False,
    )

    ai_response = Column(
        Text,
        nullable=False,
    )

    model_name = Column(
        String,
        nullable=True,
    )

    conversation_id = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
