from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)

    category = Column(String(50))
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="open")

    created_by = Column(String)
    assigned_agent_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    comments = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    timeline = relationship(
        "TicketTimeline",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )