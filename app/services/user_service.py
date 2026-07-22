from app.models.user import UserInDB
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository if repository else get_user_repository()

    async def list_users(self) -> list[UserInDB]:
        return await self.repository.list_users()

    async def get_user(self, user_id: str) -> UserInDB | None:
        return await self.repository.get_by_id(user_id)

    async def update_user(self, user_id: str, payload: UserUpdate) -> UserInDB | None:
        return await self.repository.update(
            user_id,
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            is_active=payload.is_active,
            permissions=payload.permissions,
        )

    async def delete_user(self, user_id: str) -> bool:
        return await self.repository.delete(user_id)


def get_user_service() -> UserService:
    return UserService()
