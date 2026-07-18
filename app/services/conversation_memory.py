import asyncio
from datetime import datetime

from app.schemas.conversation import ConversationState
from app.schemas.message import Message


class ConversationMemory:
    def __init__(self):
        self._conversations: dict[str, ConversationState] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(self, session_id: str, user_id: str | None = None) -> ConversationState:
        async with self._lock:
            if session_id not in self._conversations:
                self._conversations[session_id] = ConversationState(
                    session_id=session_id, user_id=user_id, messages=[], summary=None, metadata={}
                )
            return self._conversations[session_id]

    async def add_message(self, session_id: str, message: Message):
        async with self._lock:
            if session_id not in self._conversations:
                self._conversations[session_id] = ConversationState(
                    session_id=session_id, user_id=None, messages=[], summary=None, metadata={}
                )

            state = self._conversations[session_id]
            state.messages.append(message)
            state.updated_at = datetime.utcnow()

    async def update_summary(self, session_id: str, summary: str):
        async with self._lock:
            if session_id in self._conversations:
                self._conversations[session_id].summary = summary
                self._conversations[session_id].updated_at = datetime.utcnow()

    async def update_metadata(self, session_id: str, metadata: dict):
        async with self._lock:
            if session_id in self._conversations:
                self._conversations[session_id].metadata.update(metadata)
                self._conversations[session_id].updated_at = datetime.utcnow()

    async def clear_session(self, session_id: str):
        async with self._lock:
            if session_id in self._conversations:
                del self._conversations[session_id]


_conversation_memory_instance = ConversationMemory()


def get_conversation_memory() -> ConversationMemory:
    return _conversation_memory_instance
