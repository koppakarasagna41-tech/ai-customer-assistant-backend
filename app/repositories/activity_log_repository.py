from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.activity_log import ActivityLog as DBActivityLog
from app.models.activity_log import ActivityLog


class ActivityLogRepository:
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
        activity_log: ActivityLog,
    ) -> ActivityLog:
        db_activity_log = DBActivityLog(
            ticket_id=activity_log.ticket_id,
            action=activity_log.action,
            performed_by=activity_log.performed_by,
        )

        self.db.add(db_activity_log)
        self.db.commit()
        self.db.refresh(db_activity_log)

        return ActivityLog.model_validate(db_activity_log)

    async def list_by_ticket(
        self,
        ticket_id: str,
    ) -> list[ActivityLog]:
        activity_logs = (
            self.db.query(DBActivityLog)
            .filter(DBActivityLog.ticket_id == ticket_id)
            .order_by(DBActivityLog.created_at.desc())
            .all()
        )

        return [
            ActivityLog.model_validate(item)
            for item in activity_logs
        ]

    async def get_by_id(
        self,
        activity_log_id: int,
    ) -> ActivityLog | None:
        activity_log = (
            self.db.query(DBActivityLog)
            .filter(DBActivityLog.id == activity_log_id)
            .first()
        )

        if not activity_log:
            return None

        return ActivityLog.model_validate(activity_log)

    async def delete(
        self,
        activity_log_id: int,
    ) -> bool:
        activity_log = (
            self.db.query(DBActivityLog)
            .filter(DBActivityLog.id == activity_log_id)
            .first()
        )

        if not activity_log:
            return False

        self.db.delete(activity_log)
        self.db.commit()

        return True


def get_activity_log_repository() -> ActivityLogRepository:
    return ActivityLogRepository()