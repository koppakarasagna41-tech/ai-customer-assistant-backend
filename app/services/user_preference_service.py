from datetime import UTC, datetime

from app.models.user_preference import UserPreference
from app.repositories.user_preference_repository import (
    UserPreferenceRepository,
    get_user_preference_repository,
)
from app.schemas.user_preference import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
)


class UserPreferenceService:
    def __init__(
        self,
        repository: UserPreferenceRepository | None = None,
    ):
        self.repository = (
            repository
            if repository
            else get_user_preference_repository()
        )

    async def create_preference(
        self,
        data: UserPreferenceCreate,
    ) -> UserPreference:
        preference = UserPreference(
            id=0,
            user_id=data.user_id,
            theme=data.theme,
            language=data.language,
            email_notifications=data.email_notifications,
            push_notifications=data.push_notifications,
            created_at=datetime.now(UTC),
        )

        return await self.repository.create(preference)

    async def get_preference(
        self,
        user_id: str,
    ) -> UserPreference | None:
        return await self.repository.get_by_user_id(user_id)

    async def update_preference(
        self,
        user_id: str,
        data: UserPreferenceUpdate,
    ) -> UserPreference | None:
        return await self.repository.update(
            user_id,
            theme=data.theme,
            language=data.language,
            email_notifications=data.email_notifications,
            push_notifications=data.push_notifications,
        )


def get_user_preference_service() -> UserPreferenceService:
    return UserPreferenceService()