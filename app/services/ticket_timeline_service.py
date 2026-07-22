from app.models.ticket_timeline import TicketTimelineEntry
from app.repositories.ticket_timeline_repository import (
    TicketTimelineRepository,
    get_ticket_timeline_repository,
)
from app.schemas.ticket_timeline import TicketTimelineEntryCreate


class TicketTimelineService:
    def __init__(self, repository: TicketTimelineRepository | None = None):
        self.repository = repository if repository else get_ticket_timeline_repository()

    async def create_event(self, ticket_id: str, payload: TicketTimelineEntryCreate) -> TicketTimelineEntry:
        event = TicketTimelineEntry(
            event_id=f"EVT-{__import__('random').randint(10000, 99999)}",
            ticket_id=ticket_id,
            event_type=payload.event_type,
            actor=payload.actor,
            description=payload.description,
            metadata_json=payload.metadata_json,
        )
        return await self.repository.create(ticket_id, event)

    async def get_timeline(self, ticket_id: str) -> list[TicketTimelineEntry]:
        return await self.repository.get_by_ticket(ticket_id)


def get_ticket_timeline_service() -> TicketTimelineService:
    return TicketTimelineService()
