import random
from datetime import UTC, datetime
from typing import Any

from app.models.ticket import Ticket, TicketComment, TicketTimelineEvent
from app.repositories.ticket_repository import TicketRepository, get_ticket_repository
from app.schemas.filter import TicketFilterParams
from app.schemas.ticket import (
    TicketAgentAssign,
    TicketCommentCreate,
    TicketCreate,
    TicketPriorityUpdate,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.utils.ticket_validator import TicketValidator


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def _generate_ticket_id(self) -> str:
        # Generates an enterprise-format Ticket ID like TCK-48210
        num = random.randint(10000, 99999)
        return f"TCK-{num}"

    async def create_ticket(self, data: TicketCreate, actor: str = "customer") -> Ticket:
        # Validate and sanitize input fields
        TicketValidator.validate_priority(data.priority)
        sanitized_title = TicketValidator.sanitize_text(data.title)
        sanitized_desc = TicketValidator.sanitize_text(data.description)

        ticket_id = self._generate_ticket_id()
        now = datetime.now(UTC)

        timeline_event = TicketTimelineEvent(
            event_id=f"EVT-{random.randint(1000, 9999)}",
            event_type="created",
            actor=actor,
            description=f"Ticket successfully submitted by {actor}.",
            timestamp=now,
        )

        ticket = Ticket(
            ticket_id=ticket_id,
            title=sanitized_title,
            description=sanitized_desc,
            category=data.category.lower(),
            priority=data.priority.lower(),
            status="open",
            created_at=now,
            updated_at=now,
            timeline=[timeline_event],
            comments=[],
        )

        return await self.repository.create(ticket)

    async def get_ticket(self, ticket_id: str) -> Ticket:
        ticket = await self.repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with ID '{ticket_id}' not found.")
        return ticket

    async def update_ticket(
        self, ticket_id: str, data: TicketUpdate, actor: str = "system"
    ) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        now = datetime.now(UTC)

        updated_fields = []

        if data.title is not None:
            ticket.title = TicketValidator.sanitize_text(data.title)
            updated_fields.append("title")
        if data.description is not None:
            ticket.description = TicketValidator.sanitize_text(data.description)
            updated_fields.append("description")
        if data.category is not None:
            ticket.category = data.category.lower()
            updated_fields.append("category")
        if data.priority is not None:
            TicketValidator.validate_priority(data.priority)
            ticket.priority = data.priority.lower()
            updated_fields.append("priority")
        if data.status is not None:
            TicketValidator.validate_status(data.status)
            TicketValidator.validate_status_transition(ticket.status, data.status)
            ticket.status = data.status.lower()
            updated_fields.append("status")

        if updated_fields:
            ticket.updated_at = now
            event = TicketTimelineEvent(
                event_id=f"EVT-{random.randint(1000, 9999)}",
                event_type="updated",
                actor=actor,
                description=f"Updated properties: {', '.join(updated_fields)}.",
                timestamp=now,
            )
            ticket.timeline.append(event)
            await self.repository.update(ticket)

        return ticket

    async def update_status(
        self, ticket_id: str, payload: TicketStatusUpdate, actor: str
    ) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        TicketValidator.validate_status(payload.status)
        TicketValidator.validate_status_transition(ticket.status, payload.status)

        old_status = ticket.status
        ticket.status = payload.status.lower()
        now = datetime.now(UTC)
        ticket.updated_at = now

        desc = f"Status transitioned from '{old_status}' to '{payload.status}'."
        if payload.comment:
            desc += f" Reason: {payload.comment}"

        event = TicketTimelineEvent(
            event_id=f"EVT-{random.randint(1000, 9999)}",
            event_type="status_updated",
            actor=actor,
            description=desc,
            timestamp=now,
        )
        ticket.timeline.append(event)
        return await self.repository.update(ticket)

    async def update_priority(
        self, ticket_id: str, payload: TicketPriorityUpdate, actor: str
    ) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        TicketValidator.validate_priority(payload.priority)

        old_priority = ticket.priority
        ticket.priority = payload.priority.lower()
        now = datetime.now(UTC)
        ticket.updated_at = now

        desc = f"Priority escalated/changed from '{old_priority}' to '{payload.priority}'."
        if payload.comment:
            desc += f" Comment: {payload.comment}"

        event = TicketTimelineEvent(
            event_id=f"EVT-{random.randint(1000, 9999)}",
            event_type="priority_updated",
            actor=actor,
            description=desc,
            timestamp=now,
        )
        ticket.timeline.append(event)
        return await self.repository.update(ticket)

    async def assign_agent(self, ticket_id: str, payload: TicketAgentAssign, actor: str) -> Ticket:
        ticket = await self.get_ticket(ticket_id)

        old_agent = ticket.assigned_agent_id
        ticket.assigned_agent_id = payload.assigned_agent_id
        now = datetime.now(UTC)
        ticket.updated_at = now

        desc = f"Assigned to agent '{payload.assigned_agent_id}'."
        if old_agent:
            desc = f"Reassigned from '{old_agent}' to '{payload.assigned_agent_id}'."
        if payload.comment:
            desc += f" Note: {payload.comment}"

        event = TicketTimelineEvent(
            event_id=f"EVT-{random.randint(1000, 9999)}",
            event_type="agent_assigned",
            actor=actor,
            description=desc,
            timestamp=now,
        )
        ticket.timeline.append(event)
        return await self.repository.update(ticket)

    async def add_comment(self, ticket_id: str, payload: TicketCommentCreate) -> TicketComment:
        ticket = await self.get_ticket(ticket_id)
        now = datetime.now(UTC)

        comment = TicketComment(
            comment_id=f"CMT-{random.randint(1000, 9999)}",
            author=payload.author,
            content=TicketValidator.sanitize_text(payload.content),
            timestamp=now,
        )
        ticket.comments.append(comment)

        event = TicketTimelineEvent(
            event_id=f"EVT-{random.randint(1000, 9999)}",
            event_type="commented",
            actor=payload.author,
            description=f"New comment added by {payload.author}.",
            timestamp=now,
        )
        ticket.timeline.append(event)
        ticket.updated_at = now
        await self.repository.update(ticket)
        return comment

    async def delete_ticket(self, ticket_id: str) -> bool:
        # Check if ticket exists first
        await self.get_ticket(ticket_id)
        return await self.repository.delete(ticket_id)

    async def get_dashboard_stats(self) -> dict[str, Any]:
        return await self.repository.get_stats()

    async def list_tickets(
        self, filters: TicketFilterParams, page: int = 1, size: int = 10
    ) -> tuple[list[Ticket], int]:
        return await self.repository.list_and_filter(filters, page, size)


def get_ticket_service() -> TicketService:
    repo = get_ticket_repository()
    return TicketService(repository=repo)
