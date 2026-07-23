from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.database.database import Base


class AITicketClassification(Base):
    __tablename__ = "ai_ticket_classifications"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(String, nullable=False, index=True)

    predicted_category = Column(
        String,
        nullable=False,
    )

    confidence_score = Column(
        Float,
        nullable=False,
    )

    model_name = Column(
        String,
        nullable=False,
    )

    prompt_version = Column(
        String,
        nullable=True,
    )

    raw_response = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
