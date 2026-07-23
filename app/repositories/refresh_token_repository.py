import os
from contextlib import suppress
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.refresh_token import RefreshToken as DBRefreshToken
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self):
        self._memory_mode = os.getenv("DATABASE_URL") == "sqlite:///:memory:"
        self._tokens: dict[str, RefreshToken] = {}

        if not self._memory_mode:
            self.db: Session = SessionLocal()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if not self._memory_mode and hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()

    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        if self._memory_mode:
            self._tokens[refresh_token.refresh_token] = refresh_token
            return refresh_token

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
        if self._memory_mode:
            return self._tokens.get(token)

        refresh_token = (
            self.db.query(DBRefreshToken)
            .filter(DBRefreshToken.refresh_token == token)
            .first()
        )

        if not refresh_token:
            return None

        return RefreshToken.model_validate(refresh_token)

    async def revoke(
        self,
        token: str,
    ) -> bool:
        if self._memory_mode:
            refresh_token = self._tokens.get(token)
            if not refresh_token:
                return False

            refresh_token.is_revoked = True
            self._tokens[token] = refresh_token
            return True

        refresh_token = (
            self.db.query(DBRefreshToken)
            .filter(DBRefreshToken.refresh_token == token)
            .first()
        )

        if not refresh_token:
            return False

        refresh_token.is_revoked = True

        self.db.commit()
        self.db.refresh(refresh_token)

        return True

    async def delete_expired(self) -> int:
        if self._memory_mode:
            now = datetime.now(UTC)
            expired = [
                token
                for token, value in self._tokens.items()
                if value.expires_at < now
            ]

            for token in expired:
                del self._tokens[token]

            return len(expired)

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


_refresh_token_repo = RefreshTokenRepository()


def get_refresh_token_repository() -> RefreshTokenRepository:
    return _refresh_token_repo