from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class TicketTimeline(Base):
    __tablename__ = "ticket_timeline"

    event_id = Column(String, primary_key=True, index=True)

    ticket_id = Column(
        String,
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type = Column(String(50), nullable=False)
    actor = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    timestamp = Column(DateTime, server_default=func.now(), default=datetime.utcnow)

    metadata_json = Column(JSON, nullable=True, default=dict)

    ticket = relationship("Ticket", back_populates="timeline")
