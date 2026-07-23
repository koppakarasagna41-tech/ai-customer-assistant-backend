from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        String,
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"),
        nullable=False,
    )

    file_name = Column(String(255), nullable=False)

    file_path = Column(String(500), nullable=False)

    file_type = Column(String(100), nullable=False)

    file_size = Column(Integer, nullable=False)

    uploaded_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)

    ticket = relationship("Ticket")
