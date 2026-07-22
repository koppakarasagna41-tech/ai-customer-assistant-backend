from app.models.ticket_comment import TicketComment
from app.repositories.ticket_comment_repository import (
    TicketCommentRepository,
    get_ticket_comment_repository,
)
from app.schemas.ticket_comment import TicketCommentCreate, TicketCommentUpdate


class TicketCommentService:
    def __init__(self, repository: TicketCommentRepository | None = None):
        self.repository = repository if repository else get_ticket_comment_repository()

    async def create_comment(self, ticket_id: str, payload: TicketCommentCreate) -> TicketComment:
        comment = TicketComment(
            comment_id=f"CMT-{__import__('random').randint(10000, 99999)}",
            ticket_id=ticket_id,
            author=payload.author,
            content=payload.content,
        )
        return await self.repository.create(ticket_id, comment)

    async def get_comments(self, ticket_id: str) -> list[TicketComment]:
        return await self.repository.get_by_ticket(ticket_id)

    async def delete_comment(self, comment_id: str) -> bool:
        return await self.repository.delete(comment_id)


def get_ticket_comment_service() -> TicketCommentService:
    return TicketCommentService()
