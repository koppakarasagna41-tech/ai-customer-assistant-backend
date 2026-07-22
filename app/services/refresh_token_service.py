from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
    get_refresh_token_repository,
)
from app.schemas.refresh_token import RefreshTokenCreate


class RefreshTokenService:
    def __init__(
        self,
        repository: RefreshTokenRepository | None = None,
    ):
        self.repository = (
            repository
            if repository
            else get_refresh_token_repository()
        )

    async def create_refresh_token(
        self,
        data: RefreshTokenCreate,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            id=0,
            user_id=data.user_id,
            refresh_token=data.refresh_token,
            expires_at=data.expires_at,
            is_revoked=False,
            created_at=data.expires_at,
        )

        return await self.repository.create(refresh_token)

    async def get_refresh_token(
        self,
        token: str,
    ) -> RefreshToken | None:
        return await self.repository.get_by_token(token)

    async def revoke_refresh_token(
        self,
        token: str,
    ) -> bool:
        return await self.repository.revoke(token)

    async def delete_expired_tokens(
        self,
    ) -> int:
        return await self.repository.delete_expired()


def get_refresh_token_service() -> RefreshTokenService:
    return RefreshTokenService()