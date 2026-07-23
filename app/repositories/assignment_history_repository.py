from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.assignment_history import (
    AssignmentHistory as DBAssignmentHistory,
)
from app.models.assignment_history import AssignmentHistory


class AssignmentHistoryRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                

    async def create(
        self,
        assignment: AssignmentHistory,
    ) -> AssignmentHistory:
        db_assignment = DBAssignmentHistory(
            ticket_id=assignment.ticket_id,
            agent_id=assignment.agent_id,
        )

        self.db.add(db_assignment)
        self.db.commit()
        self.db.refresh(db_assignment)

        return AssignmentHistory.model_validate(db_assignment)

    async def list_by_ticket(
        self,
        ticket_id: str,
    ) -> list[AssignmentHistory]:
        assignments = (
            self.db.query(DBAssignmentHistory)
            .filter(DBAssignmentHistory.ticket_id == ticket_id)
            .order_by(DBAssignmentHistory.assigned_at.desc())
            .all()
        )

        return [AssignmentHistory.model_validate(item) for item in assignments]

    async def get_by_id(
        self,
        assignment_id: int,
    ) -> AssignmentHistory | None:
        assignment = (
            self.db.query(DBAssignmentHistory)
            .filter(DBAssignmentHistory.id == assignment_id)
            .first()
        )

        if not assignment:
            return None

        return AssignmentHistory.model_validate(assignment)

    async def delete(
        self,
        assignment_id: int,
    ) -> bool:
        assignment = (
            self.db.query(DBAssignmentHistory)
            .filter(DBAssignmentHistory.id == assignment_id)
            .first()
        )

        if not assignment:
            return False

        self.db.delete(assignment)
        self.db.commit()

        return True


def get_assignment_history_repository() -> AssignmentHistoryRepository:
    return AssignmentHistoryRepository()
