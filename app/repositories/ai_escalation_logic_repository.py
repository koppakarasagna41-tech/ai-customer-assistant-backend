from sqlalchemy.orm import Session
from contextlib import suppress
from app.database.database import SessionLocal
from app.db_models.ai_escalation_logic import (
    AIEscalationLogic as DBAIEscalationLogic,
)
from app.models.ai_escalation_logic import (
    AIEscalationLogic,
)


class AIEscalationLogicRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                

    async def create(
        self,
        escalation: AIEscalationLogic,
    ) -> AIEscalationLogic:
        db_escalation = DBAIEscalationLogic(
            ticket_id=escalation.ticket_id,
            escalation_reason=escalation.escalation_reason,
            escalation_level=escalation.escalation_level,
            assigned_team=escalation.assigned_team,
            status=escalation.status,
            auto_escalated=escalation.auto_escalated,
        )

        self.db.add(db_escalation)
        self.db.commit()
        self.db.refresh(db_escalation)

        return AIEscalationLogic.model_validate(db_escalation)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AIEscalationLogic]:
        escalations = (
            self.db.query(DBAIEscalationLogic)
            .filter(DBAIEscalationLogic.ticket_id == ticket_id)
            .order_by(DBAIEscalationLogic.created_at.desc())
            .all()
        )

        return [AIEscalationLogic.model_validate(item) for item in escalations]

    async def update(
        self,
        escalation_id: int,
        **kwargs,
    ) -> AIEscalationLogic | None:
        escalation = (
            self.db.query(DBAIEscalationLogic)
            .filter(DBAIEscalationLogic.id == escalation_id)
            .first()
        )

        if not escalation:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(escalation, key, value)

        self.db.commit()
        self.db.refresh(escalation)

        return AIEscalationLogic.model_validate(escalation)

    async def delete(
        self,
        escalation_id: int,
    ) -> bool:
        escalation = (
            self.db.query(DBAIEscalationLogic)
            .filter(DBAIEscalationLogic.id == escalation_id)
            .first()
        )

        if not escalation:
            return False

        self.db.delete(escalation)
        self.db.commit()

        return True


def get_ai_escalation_logic_repository() -> AIEscalationLogicRepository:
    return AIEscalationLogicRepository()
