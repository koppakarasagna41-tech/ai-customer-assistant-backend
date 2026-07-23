from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.conversation import Conversation as DBConversation
from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(self, conversation: Conversation) -> Conversation:
        db_item = DBConversation(
            session_id=conversation.session_id,
            user_id=conversation.user_id,
            summary=conversation.summary,
            messages=conversation.messages,
            session_metadata=conversation.session_metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return Conversation.model_validate(db_item)

    async def get_by_id(self, session_id: str) -> Conversation | None:
        row = self.db.query(DBConversation).filter(DBConversation.session_id == session_id).first()
        if not row:
            return None
        return Conversation.model_validate(row)

    async def list_by_user(self, user_id: str) -> list[Conversation]:
        rows = (
            self.db.query(DBConversation)
            .filter(DBConversation.user_id == user_id)
            .order_by(DBConversation.updated_at.desc())
            .all()
        )
        return [Conversation.model_validate(row) for row in rows]

    async def list_all(self) -> list[Conversation]:
        rows = self.db.query(DBConversation).order_by(DBConversation.updated_at.desc()).all()
        return [Conversation.model_validate(row) for row in rows]

    async def update(self, conversation: Conversation) -> Conversation:
        row = (
            self.db.query(DBConversation)
            .filter(DBConversation.session_id == conversation.session_id)
            .first()
        )
        if not row:
            raise ValueError(f"Conversation '{conversation.session_id}' not found")
        row.user_id = conversation.user_id
        row.summary = conversation.summary
        row.messages = conversation.messages
        row.session_metadata = conversation.session_metadata
        row.updated_at = conversation.updated_at
        self.db.commit()
        self.db.refresh(row)
        return Conversation.model_validate(row)

    async def delete(self, session_id: str) -> bool:
        row = self.db.query(DBConversation).filter(DBConversation.session_id == session_id).first()
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True


def get_conversation_repository() -> ConversationRepository:
    return ConversationRepository()
