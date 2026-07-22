import random
from datetime import UTC, datetime

from app.models.agent import Agent
from app.repositories.agent_repository import (
    AgentRepository,
    get_agent_repository,
)
from app.schemas.agent import AgentCreate


class AgentService:
    def __init__(
        self,
        repository: AgentRepository | None = None,
    ):
        self.repository = repository if repository else get_agent_repository()

    async def create_agent(
        self,
        data: AgentCreate,
    ) -> Agent:
        agent = Agent(
            agent_id=f"AGT-{random.randint(10000, 99999)}",
            name=data.name,
            email=data.email,
            department=data.department,
            status="available",
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(agent)

    async def get_agents(
        self,
    ) -> list[Agent]:
        return await self.repository.list_agents()

    async def get_agent(
        self,
        agent_id: str,
    ) -> Agent | None:
        return await self.repository.get_by_id(agent_id)

    async def delete_agent(
        self,
        agent_id: str,
    ) -> bool:
        return await self.repository.delete(agent_id)


def get_agent_service() -> AgentService:
    return AgentService()
