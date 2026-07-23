from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.audit_log import AuditLog as DBAuditLog
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                

    async def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:
        db_audit_log = DBAuditLog(
            entity=audit_log.entity,
            entity_id=audit_log.entity_id,
            action=audit_log.action,
            performed_by=audit_log.performed_by,
        )

        self.db.add(db_audit_log)
        self.db.commit()
        self.db.refresh(db_audit_log)

        return AuditLog.model_validate(db_audit_log)

    async def list_all(self) -> list[AuditLog]:
        audit_logs = self.db.query(DBAuditLog).order_by(DBAuditLog.created_at.desc()).all()

        return [AuditLog.model_validate(item) for item in audit_logs]

    async def get_by_id(
        self,
        audit_log_id: int,
    ) -> AuditLog | None:
        audit_log = self.db.query(DBAuditLog).filter(DBAuditLog.id == audit_log_id).first()

        if not audit_log:
            return None

        return AuditLog.model_validate(audit_log)

    async def delete(
        self,
        audit_log_id: int,
    ) -> bool:
        audit_log = self.db.query(DBAuditLog).filter(DBAuditLog.id == audit_log_id).first()

        if not audit_log:
            return False

        self.db.delete(audit_log)
        self.db.commit()

        return True


def get_audit_log_repository() -> AuditLogRepository:
    return AuditLogRepository()
