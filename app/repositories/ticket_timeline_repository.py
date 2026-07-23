from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ticket_timeline import TicketTimeline as DBTicketTimeline
from app.models.ticket_timeline import TicketTimelineEntry


class TicketTimelineRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(self, ticket_id: str, event: TicketTimelineEntry) -> TicketTimelineEntry:
        db_event = DBTicketTimeline(
            event_id=event.event_id,
            ticket_id=ticket_id,
            event_type=event.event_type,
            actor=event.actor,
            description=event.description,
            timestamp=event.timestamp,
            metadata_json=event.metadata_json,
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return TicketTimelineEntry.model_validate(db_event)

    async def get_by_ticket(self, ticket_id: str) -> list[TicketTimelineEntry]:
        timeline = (
            self.db.query(DBTicketTimeline)
            .filter(DBTicketTimeline.ticket_id == ticket_id)
            .order_by(DBTicketTimeline.timestamp.asc())
            .all()
        )
        return [TicketTimelineEntry.model_validate(item) for item in timeline]


def get_ticket_timeline_repository() -> TicketTimelineRepository:
    return TicketTimelineRepository()
