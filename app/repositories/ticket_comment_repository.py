from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.ticket_comment import TicketComment as DBTicketComment
from app.models.ticket_comment import TicketComment


class TicketCommentRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception:
                pass

    async def create(self, ticket_id: str, comment: TicketComment) -> TicketComment:
        db_comment = DBTicketComment(
            comment_id=comment.comment_id,
            ticket_id=ticket_id,
            author=comment.author,
            content=comment.content,
            timestamp=comment.timestamp,
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return TicketComment.model_validate(db_comment)

    async def get_by_ticket(self, ticket_id: str) -> list[TicketComment]:
        comments = (
            self.db.query(DBTicketComment)
            .filter(DBTicketComment.ticket_id == ticket_id)
            .order_by(DBTicketComment.timestamp.desc())
            .all()
        )
        return [TicketComment.model_validate(item) for item in comments]

    async def delete(self, comment_id: str) -> bool:
        row = self.db.query(DBTicketComment).filter(DBTicketComment.comment_id == comment_id).first()
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True


def get_ticket_comment_repository() -> TicketCommentRepository:
    return TicketCommentRepository()
