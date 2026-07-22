from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.attachment import (
    AttachmentCreate,
    AttachmentResponse,
)
from app.services.attachment_service import (
    AttachmentService,
    get_attachment_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_attachment(
    attachment: AttachmentCreate,
    service: AttachmentService = Depends(get_attachment_service),
):
    return await service.create_attachment(attachment)


@router.get(
    "/{ticket_id}",
    response_model=list[AttachmentResponse],
)
async def get_attachments(
    ticket_id: str,
    service: AttachmentService = Depends(get_attachment_service),
):
    return await service.get_attachments(ticket_id)


@router.get(
    "/details/{attachment_id}",
    response_model=AttachmentResponse,
)
async def get_attachment(
    attachment_id: int,
    service: AttachmentService = Depends(get_attachment_service),
):
    attachment = await service.get_attachment(attachment_id)

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    return attachment


@router.delete(
    "/{attachment_id}",
)
async def delete_attachment(
    attachment_id: int,
    service: AttachmentService = Depends(get_attachment_service),
):
    deleted = await service.delete_attachment(attachment_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    return {
        "success": True,
        "message": "Attachment deleted successfully",
    }
