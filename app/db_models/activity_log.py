from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.database.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        String,
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String, nullable=False)
    performed_by = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
