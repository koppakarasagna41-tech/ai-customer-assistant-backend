from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer

from app.database.database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)

    total_tickets = Column(Integer)
    resolved_tickets = Column(Integer)
    pending_tickets = Column(Integer)
    escalated_tickets = Column(Integer)

    avg_resolution_time_hrs = Column(Float)
    avg_response_time_min = Column(Float)

    customer_satisfaction_score = Column(Float)
    ai_confidence_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)