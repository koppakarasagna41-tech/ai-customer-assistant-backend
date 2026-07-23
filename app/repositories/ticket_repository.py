import asyncio
from contextlib import suppress
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ticket import Ticket as DBTicket
from app.db_models.ticket_comment import TicketComment as DBTicketComment
from app.db_models.ticket_timeline import TicketTimeline as DBTicketTimeline
from app.models.ticket import Ticket, TicketComment, TicketTimelineEvent
from app.schemas.filter import TicketFilterParams


class TicketRepository:
    def __init__(self):
        self.db: Session = SessionLocal()
        self._lock = asyncio.Lock()
        self._tickets: dict[str, Ticket] = {}
        self._seed_data()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    def _seed_data(self) -> None:
        if self._tickets:
            return

        now = datetime.now(UTC)
        timeline_event = TicketTimelineEvent(
            event_id="EVT-1001",
            event_type="created",
            actor="system",
            description="Ticket successfully submitted by customer.",
            timestamp=now,
        )
        comment = TicketComment(
            comment_id="CMT-1001",
            author="customer",
            content="Customer requested assistance.",
            timestamp=now,
        )

        self._tickets = {
            "TCK-10001": Ticket(
                ticket_id="TCK-10001",
                title="SAML login issue",
                description="Customer cannot access SSO after password reset.",
                category="technical",
                priority="urgent",
                status="open",
                assigned_agent_id="AGT-10001",
                created_at=now,
                updated_at=now,
                timeline=[timeline_event],
                comments=[comment],
            ),
            "TCK-10002": Ticket(
                ticket_id="TCK-10002",
                title="Invoice discrepancy",
                description="Customer was charged twice for the latest invoice.",
                category="billing",
                priority="high",
                status="in_progress",
                assigned_agent_id="AGT-10002",
                created_at=now,
                updated_at=now,
                timeline=[timeline_event],
                comments=[],
            ),
            "TCK-10003": Ticket(
                ticket_id="TCK-10003",
                title="Account access request",
                description="Customer needs account access restored after MFA change.",
                category="account",
                priority="medium",
                status="resolved",
                assigned_agent_id="AGT-10003",
                created_at=now,
                updated_at=now,
                timeline=[timeline_event],
                comments=[],
            ),
        }

    async def create(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.ticket_id] = ticket
        try:
            db_ticket = DBTicket(
                ticket_id=ticket.ticket_id,
                title=ticket.title,
                description=ticket.description,
                category=ticket.category,
                priority=ticket.priority,
                status=ticket.status,
                assigned_agent_id=ticket.assigned_agent_id,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
            )

            self.db.add(db_ticket)
            self.db.commit()
            self.db.refresh(db_ticket)
        except Exception:
            self.db.rollback()

        return ticket

    async def get_by_id(self, ticket_id: str) -> Ticket | None:
        if ticket_id in self._tickets:
            return self._tickets[ticket_id]

        db_ticket = self.db.query(DBTicket).filter(DBTicket.ticket_id == ticket_id).first()

        if db_ticket is None:
            return None

        ticket = Ticket(
            ticket_id=db_ticket.ticket_id,
            title=db_ticket.title,
            description=db_ticket.description,
            category=db_ticket.category,
            priority=db_ticket.priority,
            status=db_ticket.status,
            assigned_agent_id=db_ticket.assigned_agent_id,
            created_at=db_ticket.created_at,
            updated_at=db_ticket.updated_at,
            timeline=[],
            comments=[],
        )
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    async def update(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.ticket_id] = ticket

        db_ticket = self.db.query(DBTicket).filter(DBTicket.ticket_id == ticket.ticket_id).first()

        if db_ticket is None:
            raise ValueError(f"Ticket '{ticket.ticket_id}' not found")

        db_ticket.title = ticket.title
        db_ticket.description = ticket.description
        db_ticket.category = ticket.category
        db_ticket.priority = ticket.priority
        db_ticket.status = ticket.status
        db_ticket.assigned_agent_id = ticket.assigned_agent_id
        db_ticket.updated_at = ticket.updated_at

        # Save comments
        for comment in ticket.comments:
            existing_comment = (
                self.db.query(DBTicketComment)
                .filter(DBTicketComment.comment_id == comment.comment_id)
                .first()
            )

            if existing_comment is None:
                db_comment = DBTicketComment(
                    comment_id=comment.comment_id,
                    ticket_id=ticket.ticket_id,
                    author=comment.author,
                    content=comment.content,
                    timestamp=comment.timestamp,
                )
                self.db.add(db_comment)

        # Save timeline
        for event in ticket.timeline:
            existing_event = (
                self.db.query(DBTicketTimeline)
                .filter(DBTicketTimeline.event_id == event.event_id)
                .first()
            )

            if existing_event is None:
                db_event = DBTicketTimeline(
                    event_id=event.event_id,
                    ticket_id=ticket.ticket_id,
                    event_type=event.event_type,
                    actor=event.actor,
                    description=event.description,
                    timestamp=event.timestamp,
                    metadata_json={},
                )
                self.db.add(db_event)

        self.db.commit()
        self.db.refresh(db_ticket)

        return ticket

    async def delete(self, ticket_id: str) -> bool:
        self._tickets.pop(ticket_id, None)

        db_ticket = self.db.query(DBTicket).filter(DBTicket.ticket_id == ticket_id).first()

        if db_ticket is None:
            return False

        self.db.delete(db_ticket)
        self.db.commit()

        return True

    async def list_tickets(
        self,
        filters: TicketFilterParams,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Ticket], int]:
        if self._tickets:
            items = list(self._tickets.values())
            if filters.category:
                items = [item for item in items if item.category == filters.category]
            if filters.priority:
                items = [item for item in items if item.priority == filters.priority]
            if filters.status:
                items = [item for item in items if item.status == filters.status]
            if filters.assigned_agent_id:
                items = [
                    item for item in items if item.assigned_agent_id == filters.assigned_agent_id
                ]
            if filters.search_query:
                search_query = filters.search_query.lower()
                items = [
                    item
                    for item in items
                    if search_query in item.title.lower()
                    or search_query in item.description.lower()
                ]

            items.sort(
                key=lambda item: getattr(item, filters.sort_by or "created_at"),
                reverse=filters.sort_order == "desc",
            )

            total = len(items)
            paged_items = items[(page - 1) * size : page * size]
            return paged_items, total

        query = self.db.query(DBTicket)

        if filters.search_query:
            query = query.filter(
                or_(
                    DBTicket.title.ilike(f"%{filters.search_query}%"),
                    DBTicket.description.ilike(f"%{filters.search_query}%"),
                )
            )

        if filters.status:
            query = query.filter(DBTicket.status == filters.status)

        if filters.priority:
            query = query.filter(DBTicket.priority == filters.priority)

        if filters.category:
            query = query.filter(DBTicket.category == filters.category)

        if filters.assigned_agent_id:
            query = query.filter(DBTicket.assigned_agent_id == filters.assigned_agent_id)

        total = query.count()

        db_tickets = query.offset((page - 1) * size).limit(size).all()

        tickets = []
        for db_ticket in db_tickets:
            tickets.append(
                Ticket(
                    ticket_id=db_ticket.ticket_id,
                    title=db_ticket.title,
                    description=db_ticket.description,
                    category=db_ticket.category,
                    priority=db_ticket.priority,
                    status=db_ticket.status,
                    assigned_agent_id=db_ticket.assigned_agent_id,
                    created_at=db_ticket.created_at,
                    updated_at=db_ticket.updated_at,
                    timeline=[],
                    comments=[],
                )
            )

        return tickets, total

    async def list_and_filter(
        self,
        filters: TicketFilterParams,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Ticket], int]:
        return await self.list_tickets(filters, page=page, size=size)

    async def get_stats(self) -> dict[str, Any]:
        if self._tickets:
            total = len(self._tickets)
            open_count = sum(
                1 for ticket in self._tickets.values() if ticket.status.lower() == "open"
            )
            in_progress = sum(
                1 for ticket in self._tickets.values() if ticket.status.lower() == "in_progress"
            )
            resolved = sum(
                1 for ticket in self._tickets.values() if ticket.status.lower() == "resolved"
            )
            closed = sum(
                1 for ticket in self._tickets.values() if ticket.status.lower() == "closed"
            )
            high = sum(1 for ticket in self._tickets.values() if ticket.priority.lower() == "high")
            medium = sum(
                1 for ticket in self._tickets.values() if ticket.priority.lower() == "medium"
            )
            low = sum(1 for ticket in self._tickets.values() if ticket.priority.lower() == "low")
            return {
                "total": total,
                "open": open_count,
                "in_progress": in_progress,
                "resolved": resolved,
                "closed": closed,
                "high_priority": high,
                "medium_priority": medium,
                "low_priority": low,
            }

        total = self.db.query(DBTicket).count()

        open_count = self.db.query(DBTicket).filter(DBTicket.status == "Open").count()

        in_progress = self.db.query(DBTicket).filter(DBTicket.status == "In Progress").count()

        resolved = self.db.query(DBTicket).filter(DBTicket.status == "Resolved").count()

        closed = self.db.query(DBTicket).filter(DBTicket.status == "Closed").count()

        high = self.db.query(DBTicket).filter(DBTicket.priority == "High").count()

        medium = self.db.query(DBTicket).filter(DBTicket.priority == "Medium").count()

        low = self.db.query(DBTicket).filter(DBTicket.priority == "Low").count()

        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low,
        }


# Shared repository instance
_repo_instance = TicketRepository()


def get_ticket_repository() -> TicketRepository:
    return _repo_instance
