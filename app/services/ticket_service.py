import random
from datetime import UTC, datetime
from typing import Any

from app.models.ticket import Ticket, TicketComment, TicketTimelineEvent
from app.repositories.ticket_repository import TicketRepository, get_ticket_repository
from app.schemas.ai_confidence_score import (
    AIConfidenceScoreCreate,
)
from app.schemas.ai_conversation_history import (
    AIConversationHistoryCreate,
)
from app.schemas.ai_escalation_logic import (
    AIEscalationLogicCreate,
)
from app.schemas.ai_priority_prediction import (
    AIPriorityPredictionCreate,
)
from app.schemas.ai_suggested_response import (
    AISuggestedResponseCreate,
)
from app.schemas.ai_ticket_classification import (
    AITicketClassificationCreate,
)
from app.schemas.filter import TicketFilterParams
from app.schemas.ticket import (
    TicketAgentAssign,
    TicketCommentCreate,
    TicketCreate,
    TicketPriorityUpdate,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.ai_confidence_score_service import (
    AIConfidenceScoreService,
)
from app.services.ai_conversation_history_service import (
    AIConversationHistoryService,
)
from app.services.ai_escalation_logic_service import (
    AIEscalationLogicService,
)
from app.services.ai_priority_prediction_service import (
    AIPriorityPredictionService,
)
from app.services.ai_suggested_response_service import (
    AISuggestedResponseService,
)
from app.services.ai_ticket_classification_service import (
    AITicketClassificationService,
)
from app.services.gemini_service import get_gemini_service
from app.utils.ticket_validator import TicketValidator


class TicketService:
    def __init__(
        self,
        repository: TicketRepository | None = None,
    ):
        self.repository = repository if repository else get_ticket_repository()

        self.ai_classification_service = AITicketClassificationService()

        self.ai_priority_service = AIPriorityPredictionService()

        self.ai_response_service = AISuggestedResponseService()
        self.ai_confidence_service = AIConfidenceScoreService()
        self.ai_escalation_service = AIEscalationLogicService()
        self.ai_conversation_service = AIConversationHistoryService()
        self.gemini_service = get_gemini_service()

    def _generate_ticket_id(self) -> str:
        # Generates an enterprise-format Ticket ID like TCK-48210
        num = random.randint(10000, 99999)
        return f"TCK-{num}"

    async def create_ticket(
        self,
        data: TicketCreate,
        actor: str = "customer",
    ) -> Ticket:
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

        created_ticket = await self.repository.create(ticket)

        ai_result = await self.gemini_service.analyze_ticket(
            created_ticket.title,
            created_ticket.description,
        )

        await self.ai_classification_service.create_classification(
            AITicketClassificationCreate(
                ticket_id=created_ticket.ticket_id,
                predicted_category=ai_result["predicted_category"],
                confidence_score=ai_result["confidence_score"],
                model_name="gemini-2.5-flash",
                prompt_version="v1",
                raw_response=str(ai_result),
            )
        )

        await self.ai_priority_service.create_prediction(
            AIPriorityPredictionCreate(
                ticket_id=created_ticket.ticket_id,
                predicted_priority=ai_result["predicted_priority"],
                confidence_score=ai_result["confidence_score"],
                model_name="gemini-2.5-flash",
                prompt_version="v1",
                raw_response=str(ai_result),
            )
        )

        await self.ai_response_service.create_response(
            AISuggestedResponseCreate(
                ticket_id=created_ticket.ticket_id,
                suggested_response=ai_result["suggested_response"],
                confidence_score=ai_result["confidence_score"],
                model_name="gemini-2.5-flash",
                prompt_version="v1",
                status="generated",
            )
        )

        await self.ai_confidence_service.create_confidence_score(
            AIConfidenceScoreCreate(
                ticket_id=created_ticket.ticket_id,
                confidence_score=ai_result["confidence_score"],
                prediction_type="overall",
                model_name="gemini-flash-latest",
            )
        )
        await self.ai_conversation_service.create_conversation(
            AIConversationHistoryCreate(
                ticket_id=created_ticket.ticket_id,
                user_message=created_ticket.description,
                ai_response=ai_result["suggested_response"],
                model_name="gemini-flash-latest",
                conversation_id=created_ticket.ticket_id,
            )
        )

        should_escalate = (
            ai_result["predicted_priority"].lower() == "high"
            or ai_result["confidence_score"] < 0.70
        )

        if should_escalate:
            await self.ai_escalation_service.create_escalation(
                AIEscalationLogicCreate(
                    ticket_id=created_ticket.ticket_id,
                    escalation_reason=(
                        "High priority ticket"
                        if ai_result["predicted_priority"].lower() == "high"
                        else "Low AI confidence"
                    ),
                    escalation_level="Level 1",
                    assigned_team="Support Team",
                    status="pending",
                    auto_escalated=True,
                )
            )

        return created_ticket

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

        desc = f"Priority escalated/changed from '{old_priority}' " f"to '{payload.priority}'."
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

    async def assign_agent(
        self,
        ticket_id: str,
        payload: TicketAgentAssign,
        actor: str,
    ) -> Ticket:
        ticket = await self.get_ticket(ticket_id)

        old_agent = ticket.assigned_agent_id
        ticket.assigned_agent_id = payload.assigned_agent_id
        now = datetime.now(UTC)
        ticket.updated_at = now

        desc = f"Assigned to agent '{payload.assigned_agent_id}'."
        if old_agent:
            desc = f"Reassigned from '{old_agent}' " f"to '{payload.assigned_agent_id}'."
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

    async def add_comment(
        self,
        ticket_id: str,
        payload: TicketCommentCreate,
    ) -> TicketComment:
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
        self,
        filters: TicketFilterParams,
        page: int = 1,
        size: int = 10,
    ):
        return await self.repository.list_and_filter(
            filters,
            page,
            size,
        )


def get_ticket_service() -> TicketService:
    repo = get_ticket_repository()
    return TicketService(repository=repo)
