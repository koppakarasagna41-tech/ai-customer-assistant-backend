from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.database.database import Base


class AIEscalationLogic(Base):
    __tablename__ = "ai_escalation_logic"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        String,
        nullable=False,
    )

    escalation_reason = Column(
        Text,
        nullable=False,
    )

    escalation_level = Column(
        String,
        nullable=False,
    )

    assigned_team = Column(
        String,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
    )

    auto_escalated = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
