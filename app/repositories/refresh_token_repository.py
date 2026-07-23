from contextlib import suppress

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.refresh_token import (
    RefreshToken as DBRefreshToken,
)
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        db_refresh_token = DBRefreshToken(
            user_id=refresh_token.user_id,
            refresh_token=refresh_token.refresh_token,
            expires_at=refresh_token.expires_at,
            is_revoked=refresh_token.is_revoked,
        )

        self.db.add(db_refresh_token)
        self.db.commit()
        self.db.refresh(db_refresh_token)

        return RefreshToken.model_validate(db_refresh_token)

    async def get_by_token(
        self,
        token: str,
    ) -> RefreshToken | None:
        refresh_token = (
            self.db.query(DBRefreshToken).filter(DBRefreshToken.refresh_token == token).first()
        )

        if not refresh_token:
            return None

        return RefreshToken.model_validate(refresh_token)

    async def revoke(
        self,
        token: str,
    ) -> bool:
        refresh_token = (
            self.db.query(DBRefreshToken).filter(DBRefreshToken.refresh_token == token).first()
        )

        if not refresh_token:
            return False

        refresh_token.is_revoked = True

        self.db.commit()
        self.db.refresh(refresh_token)

        return True

    async def delete_expired(self) -> int:
        from datetime import UTC, datetime

        expired_tokens = (
            self.db.query(DBRefreshToken)
            .filter(DBRefreshToken.expires_at < datetime.now(UTC))
            .all()
        )

        count = len(expired_tokens)

        for token in expired_tokens:
            self.db.delete(token)

        self.db.commit()

        return count


def get_refresh_token_repository() -> RefreshTokenRepository:
    return RefreshTokenRepository()
