from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.database import Base


class AIConfidenceScore(Base):
    __tablename__ = "ai_confidence_scores"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        String,
        nullable=False,
    )

    confidence_score = Column(
        Float,
        nullable=False,
    )

    prediction_type = Column(
        String,
        nullable=False,
    )

    model_name = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
