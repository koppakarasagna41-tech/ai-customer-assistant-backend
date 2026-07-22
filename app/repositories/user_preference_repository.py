from sqlalchemy.orm import Session
from contextlib import suppress
from app.database.database import SessionLocal
from app.db_models.user_preference import (
    UserPreference as DBUserPreference,
)
from app.models.user_preference import UserPreference


class UserPreferenceRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(
        self,
        preference: UserPreference,
    ) -> UserPreference:
        db_preference = DBUserPreference(
            user_id=preference.user_id,
            theme=preference.theme,
            language=preference.language,
            email_notifications=preference.email_notifications,
            push_notifications=preference.push_notifications,
        )

        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)

        return UserPreference.model_validate(db_preference)

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> UserPreference | None:
        preference = (
            self.db.query(DBUserPreference).filter(DBUserPreference.user_id == user_id).first()
        )

        if not preference:
            return None

        return UserPreference.model_validate(preference)

    async def update(
        self,
        user_id: str,
        **kwargs,
    ) -> UserPreference | None:
        preference = (
            self.db.query(DBUserPreference).filter(DBUserPreference.user_id == user_id).first()
        )

        if not preference:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(preference, key, value)

        self.db.commit()
        self.db.refresh(preference)

        return UserPreference.model_validate(preference)


def get_user_preference_repository() -> UserPreferenceRepository:
    return UserPreferenceRepository()
