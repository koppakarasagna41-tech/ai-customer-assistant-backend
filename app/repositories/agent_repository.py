import random

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.agent import Agent as DBAgent
from app.models.agent import Agent


class AgentRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception:
                pass

    async def create(
        self,
        agent: Agent,
    ) -> Agent:
        db_agent = DBAgent(
            agent_id=f"AGT-{random.randint(10000, 99999)}",
            name=agent.name,
            email=agent.email,
            department=agent.department,
            status=agent.status,
        )

        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)

        return Agent.model_validate(db_agent)

    async def list_agents(
        self,
    ) -> list[Agent]:
        agents = (
            self.db.query(DBAgent)
            .order_by(DBAgent.created_at.desc())
            .all()
        )

        return [
            Agent.model_validate(agent)
            for agent in agents
        ]

    async def get_by_id(
        self,
        agent_id: str,
    ) -> Agent | None:
        agent = (
            self.db.query(DBAgent)
            .filter(DBAgent.agent_id == agent_id)
            .first()
        )

        if not agent:
            return None

        return Agent.model_validate(agent)

    async def delete(
        self,
        agent_id: str,
    ) -> bool:
        agent = (
            self.db.query(DBAgent)
            .filter(DBAgent.agent_id == agent_id)
            .first()
        )

        if not agent:
            return False

        self.db.delete(agent)
        self.db.commit()

        return True


def get_agent_repository() -> AgentRepository:
    return AgentRepository()