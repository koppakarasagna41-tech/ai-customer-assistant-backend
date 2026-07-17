import asyncio
from datetime import UTC, datetime
from typing import Any

from app.models.ticket import Ticket, TicketComment, TicketTimelineEvent
from app.schemas.filter import SortOrder, TicketFilterParams


class TicketRepository:
    def __init__(self):
        self._tickets: dict[str, Ticket] = {}
        self._lock = asyncio.Lock()
        self._seed_data()

    def _seed_data(self):
        # Seed some enterprise tickets for testing
        now = datetime.now(UTC)
        self._tickets["TCK-10001"] = Ticket(
            ticket_id="TCK-10001",
            title="Unable to process subscription payment via Mastercard",
            description=(
                "Every time I try to renew my subscription, I receive a "
                "Gateway Timeout error on checkout."
            ),
            category="billing",
            priority="high",
            status="in_progress",
            assigned_agent_id="AGT-55412",
            created_at=now,
            updated_at=now,
            timeline=[
                TicketTimelineEvent(
                    event_id="EVT-001",
                    event_type="created",
                    actor="system",
                    description="Ticket automatically created on customer ingestion.",
                    timestamp=now,
                ),
                TicketTimelineEvent(
                    event_id="EVT-002",
                    event_type="agent_assigned",
                    actor="admin",
                    description="Assigned to billing representative (AGT-55412).",
                    timestamp=now,
                ),
            ],
            comments=[
                TicketComment(
                    comment_id="CMT-001",
                    author="AGT-55412",
                    content="Checking with the gateway provider now. Will update soon.",
                    timestamp=now,
                )
            ],
        )
        self._tickets["TCK-10002"] = Ticket(
            ticket_id="TCK-10002",
            title="SSO Integration failure for Okta identity provider",
            description=(
                "Users from my team are redirected to a blank screen after "
                "successful authentication in Okta."
            ),
            category="technical",
            priority="urgent",
            status="open",
            created_at=now,
            updated_at=now,
            timeline=[
                TicketTimelineEvent(
                    event_id="EVT-003",
                    event_type="created",
                    actor="customer",
                    description="Ticket created by Okta administrator.",
                    timestamp=now,
                )
            ],
        )
        self._tickets["TCK-10003"] = Ticket(
            ticket_id="TCK-10003",
            title="General inquiry about custom enterprise SLA details",
            description=(
                "Could you provide the exact response and resolution target "
                "times for custom SLAs?"
            ),
            category="account",
            priority="low",
            status="closed",
            assigned_agent_id="AGT-11002",
            created_at=now,
            updated_at=now,
            timeline=[
                TicketTimelineEvent(
                    event_id="EVT-004",
                    event_type="created",
                    actor="customer",
                    description="Ticket created from portal query.",
                    timestamp=now,
                ),
                TicketTimelineEvent(
                    event_id="EVT-005",
                    event_type="status_updated",
                    actor="AGT-11002",
                    description="Resolved and closed after sharing the SLA brochure.",
                    timestamp=now,
                ),
            ],
        )

    async def create(self, ticket: Ticket) -> Ticket:
        async with self._lock:
            self._tickets[ticket.ticket_id] = ticket
            return ticket

    async def get_by_id(self, ticket_id: str) -> Ticket | None:
        async with self._lock:
            return self._tickets.get(ticket_id)

    async def update(self, ticket: Ticket) -> Ticket:
        async with self._lock:
            ticket.updated_at = datetime.now(UTC)
            self._tickets[ticket.ticket_id] = ticket
            return ticket

    async def delete(self, ticket_id: str) -> bool:
        async with self._lock:
            if ticket_id in self._tickets:
                del self._tickets[ticket_id]
                return True
            return False

    async def list_and_filter(
        self, filters: TicketFilterParams, page: int = 1, size: int = 10
    ) -> tuple[list[Ticket], int]:
        async with self._lock:
            matched_tickets = list(self._tickets.values())

            # Apply filters
            if filters.category:
                matched_tickets = [
                    t for t in matched_tickets if t.category.lower() == filters.category.lower()
                ]
            if filters.priority:
                matched_tickets = [
                    t for t in matched_tickets if t.priority.lower() == filters.priority.lower()
                ]
            if filters.status:
                matched_tickets = [
                    t for t in matched_tickets if t.status.lower() == filters.status.lower()
                ]
            if filters.assigned_agent_id:
                matched_tickets = [
                    t for t in matched_tickets if t.assigned_agent_id == filters.assigned_agent_id
                ]
            if filters.search_query:
                q = filters.search_query.lower()
                matched_tickets = [
                    t
                    for t in matched_tickets
                    if q in t.title.lower()
                    or q in t.description.lower()
                    or q in t.ticket_id.lower()
                ]

            # Apply Sorting
            sort_by = filters.sort_by or "created_at"
            reverse = filters.sort_order == SortOrder.DESC

            def sort_key(t: Ticket):
                val = getattr(t, sort_by, None)
                if val is None:
                    return ""
                return val

            matched_tickets.sort(key=sort_key, reverse=reverse)

            total = len(matched_tickets)
            start = (page - 1) * size
            end = start + size
            items = matched_tickets[start:end]

            return items, total

    async def get_stats(self) -> dict[str, Any]:
        async with self._lock:
            tickets = list(self._tickets.values())

            stats = {
                "total_count": len(tickets),
                "open_count": sum(1 for t in tickets if t.status == "open"),
                "in_progress_count": sum(1 for t in tickets if t.status == "in_progress"),
                "closed_count": sum(1 for t in tickets if t.status == "closed"),
                "escalated_count": sum(1 for t in tickets if t.status == "escalated"),
                "distribution_by_priority": {},
                "distribution_by_category": {},
            }

            for t in tickets:
                p = t.priority
                stats["distribution_by_priority"][p] = (
                    stats["distribution_by_priority"].get(p, 0) + 1
                )
                c = t.category
                stats["distribution_by_category"][c] = (
                    stats["distribution_by_category"].get(c, 0) + 1
                )

            return stats


# Shared global repository instance for in-memory storage
_repo_instance = TicketRepository()


def get_ticket_repository() -> TicketRepository:
    return _repo_instance
