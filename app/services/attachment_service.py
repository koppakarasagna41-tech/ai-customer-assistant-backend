from app.models.attachment import Attachment
from app.repositories.attachment_repository import (
    AttachmentRepository,
    get_attachment_repository,
)
from app.schemas.attachment import AttachmentCreate


class AttachmentService:
    def __init__(
        self,
        repository: AttachmentRepository | None = None,
    ):
        self.repository = repository if repository else get_attachment_repository()

    async def create_attachment(
        self,
        data: AttachmentCreate,
    ) -> Attachment:
        attachment = Attachment(
            ticket_id=data.ticket_id,
            file_name=data.file_name,
            file_path=data.file_path,
            file_type=data.file_type,
            file_size=data.file_size,
        )

        return await self.repository.create(attachment)

    async def get_attachments(
        self,
        ticket_id: str,
    ) -> list[Attachment]:
        return await self.repository.list_by_ticket(ticket_id)

    async def get_attachment(
        self,
        attachment_id: int,
    ) -> Attachment | None:
        return await self.repository.get_by_id(attachment_id)

    async def delete_attachment(
        self,
        attachment_id: int,
    ) -> bool:
        return await self.repository.delete(attachment_id)


def get_attachment_service() -> AttachmentService:
    return AttachmentService()
