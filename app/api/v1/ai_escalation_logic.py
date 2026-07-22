from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_escalation_logic import (
    AIEscalationLogicCreate,
    AIEscalationLogicResponse,
    AIEscalationLogicUpdate,
)
from app.services.ai_escalation_logic_service import (
    AIEscalationLogicService,
    get_ai_escalation_logic_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIEscalationLogicResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_escalation(
    data: AIEscalationLogicCreate,
    service: AIEscalationLogicService = Depends(get_ai_escalation_logic_service),
):
    return await service.create_escalation(data)


@router.get(
    "/{ticket_id}",
    response_model=list[AIEscalationLogicResponse],
)
async def get_escalations(
    ticket_id: str,
    service: AIEscalationLogicService = Depends(get_ai_escalation_logic_service),
):
    return await service.get_escalations(ticket_id)


@router.put(
    "/{escalation_id}",
    response_model=AIEscalationLogicResponse,
)
async def update_escalation(
    escalation_id: int,
    data: AIEscalationLogicUpdate,
    service: AIEscalationLogicService = Depends(get_ai_escalation_logic_service),
):
    escalation = await service.update_escalation(
        escalation_id,
        data,
    )

    if not escalation:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    return escalation


@router.delete(
    "/{escalation_id}",
)
async def delete_escalation(
    escalation_id: int,
    service: AIEscalationLogicService = Depends(get_ai_escalation_logic_service),
):
    deleted = await service.delete_escalation(escalation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    return {"message": "Escalation deleted successfully"}
