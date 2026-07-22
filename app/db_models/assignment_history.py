from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AssignmentHistory(Base):
    __tablename__ = "assignment_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    ticket_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
    )

    agent_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("agents.agent_id"),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
