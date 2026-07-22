import random
from datetime import UTC, datetime, timedelta

from app.models.refresh_token import RefreshToken as RefreshTokenModel
from app.models.user import User, UserInDB
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
    get_refresh_token_repository,
)
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.auth import LoginCredentials
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.security.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    JWTManager,
)
from app.security.password import PasswordHasher
from app.security.permissions import ROLE_PERMISSIONS


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.repository = repository
        self.refresh_token_repository = refresh_token_repository

    def _generate_user_id(self) -> str:
        num = random.randint(10000, 99999)
        return f"USR-{num}"

    async def register_user(self, data: UserCreate) -> User:
        # Check if username or email already exists
        existing_username = await self.repository.get_by_username(data.username)
        if existing_username:
            raise ValueError(f"Username '{data.username}' is already taken.")

        existing_email = await self.repository.get_by_email(data.email)
        if existing_email:
            raise ValueError(f"Email '{data.email}' is already registered.")

        # Validate role
        valid_roles = {"customer", "support_agent", "support_admin", "supervisor", "system_admin"}
        role = data.role.lower()
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{data.role}'. Must be one of {valid_roles}")

        user_id = self._generate_user_id()
        now = datetime.now(UTC)
        hashed_password = PasswordHasher.hash_password(data.password)
        perms = [p.value for p in ROLE_PERMISSIONS.get(role, [])]

        user_in_db = UserInDB(
            user_id=user_id,
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
            permissions=perms,
            hashed_password=hashed_password,
        )

        created_user = await self.repository.create(user_in_db)
        return User(**created_user.dict())

    async def authenticate_user(self, credentials: LoginCredentials) -> User:
        # Try finding by username first, then by email
        user = await self.repository.get_by_username(credentials.username_or_email)
        if not user:
            user = await self.repository.get_by_email(credentials.username_or_email)

        if not user:
            raise ValueError("Invalid username/email or password.")

        if not user.is_active:
            raise ValueError("This user account is deactivated.")

        if not PasswordHasher.verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid username/email or password.")

        return User(**user.dict())

    async def login(self, credentials: LoginCredentials) -> Token:
        user = await self.authenticate_user(credentials)

        token_data = {"sub": user.user_id, "role": user.role, "username": user.username}

        access_token = JWTManager.create_access_token(token_data)
        refresh_token = JWTManager.create_refresh_token(token_data)

        # Store refresh token in database for rotation tracking
        expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_model = RefreshTokenModel(
            user_id=user.user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self.refresh_token_repository.create(refresh_token_model)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        # Check if token exists and is not revoked
        stored_token = await self.refresh_token_repository.get_by_token(refresh_token)
        if not stored_token or stored_token.is_revoked:
            raise ValueError("Refresh token is invalid or has been revoked.")

        # Check if token is expired
        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise ValueError("Refresh token has expired.")

        try:
            payload = JWTManager.decode_token(refresh_token)
        except ValueError as exc:
            raise ValueError(f"Invalid refresh token: {exc!s}") from exc

        if payload.get("type") != "refresh":
            raise ValueError("Token provided is not a refresh token.")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid refresh token payload.")

        user = await self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User associated with this refresh token is inactive or not found.")

        token_data = {"sub": user.user_id, "role": user.role, "username": user.username}

        access_token = JWTManager.create_access_token(token_data)
        new_refresh_token = JWTManager.create_refresh_token(token_data)

        # Revoke old refresh token and store new one
        await self.refresh_token_repository.revoke(refresh_token)
        
        expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token_model = RefreshTokenModel(
            user_id=user.user_id,
            refresh_token=new_refresh_token,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self.refresh_token_repository.create(new_refresh_token_model)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )


def get_auth_service() -> AuthService:
    user_repo = get_user_repository()
    refresh_token_repo = get_refresh_token_repository()
    return AuthService(repository=user_repo, refresh_token_repository=refresh_token_repo)
