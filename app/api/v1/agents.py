from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.agent import AgentCreate, AgentResponse
from app.services.agent_service import (
    AgentService,
    get_agent_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    agent: AgentCreate,
    service: AgentService = Depends(get_agent_service),
):
    return await service.create_agent(agent)


@router.get(
    "/",
    response_model=list[AgentResponse],
)
async def get_agents(
    service: AgentService = Depends(get_agent_service),
):
    return await service.get_agents()


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
async def get_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service),
):
    agent = await service.get_agent(agent_id)

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.delete(
    "/{agent_id}",
)
async def delete_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service),
):
    deleted = await service.delete_agent(agent_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return {
        "success": True,
        "message": "Agent deleted successfully",
    }