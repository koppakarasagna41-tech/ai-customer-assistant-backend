from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.audit_log import (
    AuditLogCreate,
    AuditLogResponse,
)
from app.services.audit_log_service import (
    AuditLogService,
    get_audit_log_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_log(
    audit_log: AuditLogCreate,
    service: AuditLogService = Depends(
        get_audit_log_service,
    ),
):
    return await service.create_audit_log(audit_log)


@router.get(
    "/",
    response_model=list[AuditLogResponse],
)
async def get_audit_logs(
    service: AuditLogService = Depends(
        get_audit_log_service,
    ),
):
    return await service.get_audit_logs()


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
async def get_audit_log(
    audit_log_id: int,
    service: AuditLogService = Depends(
        get_audit_log_service,
    ),
):
    audit_log = await service.get_audit_log(audit_log_id)

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return audit_log


@router.delete(
    "/{audit_log_id}",
)
async def delete_audit_log(
    audit_log_id: int,
    service: AuditLogService = Depends(
        get_audit_log_service,
    ),
):
    deleted = await service.delete_audit_log(audit_log_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return {
        "success": True,
        "message": "Audit log deleted successfully",
    }
