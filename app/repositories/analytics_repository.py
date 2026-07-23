from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.analytics import Analytics as DBAnalytics
from app.models.analytics import Analytics


class AnalyticsRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                

    async def create(self, analytics: Analytics) -> Analytics:
        db_item = DBAnalytics(
            total_tickets=analytics.total_tickets,
            resolved_tickets=analytics.resolved_tickets,
            pending_tickets=analytics.pending_tickets,
            escalated_tickets=analytics.escalated_tickets,
            avg_resolution_time_hrs=analytics.avg_resolution_time_hrs,
            avg_response_time_min=analytics.avg_response_time_min,
            customer_satisfaction_score=analytics.customer_satisfaction_score,
            ai_confidence_score=analytics.ai_confidence_score,
            created_at=analytics.created_at,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return Analytics.model_validate(db_item)

    async def get_latest(self) -> Analytics | None:
        row = self.db.query(DBAnalytics).order_by(DBAnalytics.created_at.desc()).first()
        if not row:
            return None
        return Analytics.model_validate(row)

    async def list_all(self) -> list[Analytics]:
        rows = self.db.query(DBAnalytics).order_by(DBAnalytics.created_at.desc()).all()
        return [Analytics.model_validate(row) for row in rows]


def get_analytics_repository() -> AnalyticsRepository:
    return AnalyticsRepository()
