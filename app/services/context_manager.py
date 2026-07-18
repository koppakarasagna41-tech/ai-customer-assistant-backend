import logging
from typing import Any

from app.repositories.ticket_repository import get_ticket_repository

logger = logging.getLogger("app.services.context_manager")


class ContextManager:
    def __init__(self):
        self.ticket_repo = get_ticket_repository()

    async def build_enriched_context(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        client_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Gathers system context such as active tickets for the user, user details,
        and combines them with client-side metadata to feed into the prompt builder.
        """
        context: dict[str, Any] = {
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": "2026-07-16T12:29:00Z",
        }

        if client_metadata:
            context.update(client_metadata)

        # Retrieve active tickets if user_id is provided
        if user_id:
            try:
                # Get user's tickets if possible or provide general stats
                tickets, _ = await self.ticket_repo.list_and_filter(filters=None, page=1, size=10)
                user_tickets = [
                    {
                        "ticket_id": t.ticket_id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                        "category": t.category,
                    }
                    for t in tickets
                    if getattr(t, "user_id", None) == user_id or t.status == "open"
                ]
                context["active_tickets"] = user_tickets[:5]  # Limit to top 5
            except Exception as e:
                logger.warning(f"Failed to fetch tickets for context builder: {e}")
                context["active_tickets"] = []

        return context
