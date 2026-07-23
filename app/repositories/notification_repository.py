from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.notification import Notification as DBNotification
from app.models.notification import Notification


class NotificationRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(self, notification: Notification) -> Notification:
        db_notification = DBNotification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            is_read=notification.is_read,
        )

        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)

        return Notification.model_validate(db_notification)

    async def list_by_user(self, user_id: str) -> list[Notification]:
        notifications = (
            self.db.query(DBNotification)
            .filter(DBNotification.user_id == user_id)
            .order_by(DBNotification.created_at.desc())
            .all()
        )

        return [Notification.model_validate(notification) for notification in notifications]

    async def get_by_id(self, notification_id: int) -> Notification | None:
        notification = (
            self.db.query(DBNotification).filter(DBNotification.id == notification_id).first()
        )

        if not notification:
            return None

        return Notification.model_validate(notification)

    async def mark_as_read(self, notification_id: int) -> Notification | None:
        notification = (
            self.db.query(DBNotification).filter(DBNotification.id == notification_id).first()
        )

        if not notification:
            return None

        notification.is_read = True

        self.db.commit()
        self.db.refresh(notification)

        return Notification.model_validate(notification)

    async def delete(self, notification_id: int) -> bool:
        notification = (
            self.db.query(DBNotification).filter(DBNotification.id == notification_id).first()
        )

        if not notification:
            return False

        self.db.delete(notification)
        self.db.commit()

        return True


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()
