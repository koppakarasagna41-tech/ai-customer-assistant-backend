from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.database.database import Base


class AIPromptManagement(Base):
    __tablename__ = "ai_prompt_management"

    id = Column(Integer, primary_key=True, index=True)

    prompt_name = Column(
        String,
        nullable=False,
    )

    prompt_template = Column(
        Text,
        nullable=False,
    )

    prompt_version = Column(
        String,
        nullable=False,
    )

    model_name = Column(
        String,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )