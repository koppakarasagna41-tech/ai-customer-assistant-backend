from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ai_conversation_history import (
    AIConversationHistory as DBAIConversationHistory,
)
from app.models.ai_conversation_history import (
    AIConversationHistory,
)


class AIConversationHistoryRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(
        self,
        conversation: AIConversationHistory,
    ) -> AIConversationHistory:
        db_conversation = DBAIConversationHistory(
            ticket_id=conversation.ticket_id,
            user_message=conversation.user_message,
            ai_response=conversation.ai_response,
            model_name=conversation.model_name,
            conversation_id=conversation.conversation_id,
        )

        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)

        return AIConversationHistory.model_validate(db_conversation)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AIConversationHistory]:
        conversations = (
            self.db.query(DBAIConversationHistory)
            .filter(DBAIConversationHistory.ticket_id == ticket_id)
            .order_by(DBAIConversationHistory.created_at.asc())
            .all()
        )

        return [AIConversationHistory.model_validate(item) for item in conversations]

    async def update(
        self,
        conversation_id: int,
        **kwargs,
    ) -> AIConversationHistory | None:
        conversation = (
            self.db.query(DBAIConversationHistory)
            .filter(DBAIConversationHistory.id == conversation_id)
            .first()
        )

        if not conversation:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(conversation, key, value)

        self.db.commit()
        self.db.refresh(conversation)

        return AIConversationHistory.model_validate(conversation)

    async def delete(
        self,
        conversation_id: int,
    ) -> bool:
        conversation = (
            self.db.query(DBAIConversationHistory)
            .filter(DBAIConversationHistory.id == conversation_id)
            .first()
        )

        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True


def get_ai_conversation_history_repository() -> AIConversationHistoryRepository:
    return AIConversationHistoryRepository()
