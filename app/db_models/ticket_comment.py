from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    comment_id = Column(String, primary_key=True, index=True)

    ticket_id = Column(
        String,
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"),
        nullable=False,
    )

    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    
    ticket = relationship("Ticket", back_populates="comments")