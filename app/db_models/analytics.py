from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, func

from app.database.database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)

    total_tickets = Column(Integer, nullable=True)
    resolved_tickets = Column(Integer, nullable=True)
    pending_tickets = Column(Integer, nullable=True)
    escalated_tickets = Column(Integer, nullable=True)

    avg_resolution_time_hrs = Column(Float, nullable=True)
    avg_response_time_min = Column(Float, nullable=True)

    customer_satisfaction_score = Column(Float, nullable=True)
    ai_confidence_score = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)
