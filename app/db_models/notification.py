from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False, index=True)

    title = Column(String(200), nullable=False)

    message = Column(Text, nullable=False)

    type = Column(String(50), default="info", nullable=False)

    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.utcnow,
    )
