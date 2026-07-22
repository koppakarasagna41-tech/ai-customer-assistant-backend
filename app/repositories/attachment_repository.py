from sqlalchemy.orm import Session
from contextlib import suppress
from app.database.database import SessionLocal
from app.db_models.attachment import Attachment as DBAttachment
from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(self, attachment: Attachment) -> Attachment:
        db_attachment = DBAttachment(
            ticket_id=attachment.ticket_id,
            file_name=attachment.file_name,
            file_path=attachment.file_path,
            file_type=attachment.file_type,
            file_size=attachment.file_size,
        )

        self.db.add(db_attachment)
        self.db.commit()
        self.db.refresh(db_attachment)

        return Attachment.model_validate(db_attachment)

    async def list_by_ticket(
        self,
        ticket_id: str,
    ) -> list[Attachment]:
        attachments = (
            self.db.query(DBAttachment)
            .filter(DBAttachment.ticket_id == ticket_id)
            .order_by(DBAttachment.uploaded_at.desc())
            .all()
        )

        return [Attachment.model_validate(attachment) for attachment in attachments]

    async def get_by_id(
        self,
        attachment_id: int,
    ) -> Attachment | None:
        attachment = self.db.query(DBAttachment).filter(DBAttachment.id == attachment_id).first()

        if not attachment:
            return None

        return Attachment.model_validate(attachment)

    async def delete(
        self,
        attachment_id: int,
    ) -> bool:
        attachment = self.db.query(DBAttachment).filter(DBAttachment.id == attachment_id).first()

        if not attachment:
            return False

        self.db.delete(attachment)
        self.db.commit()

        return True


def get_attachment_repository() -> AttachmentRepository:
    return AttachmentRepository()
