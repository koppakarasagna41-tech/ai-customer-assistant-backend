import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import User, UserInDB
from app.schemas.user import UserCreate
from app.schemas.auth import LoginCredentials
from app.schemas.token import Token
from app.security.password import PasswordHasher
from app.security.jwt import JWTManager, ACCESS_TOKEN_EXPIRE_MINUTES
from app.security.permissions import ROLE_PERMISSIONS

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

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
        now = datetime.now(timezone.utc)
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
            hashed_password=hashed_password
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
        
        token_data = {
            "sub": user.user_id,
            "role": user.role,
            "username": user.username
        }
        
        access_token = JWTManager.create_access_token(token_data)
        refresh_token = JWTManager.create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        try:
            payload = JWTManager.decode_token(refresh_token)
        except ValueError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")

        if payload.get("type") != "refresh":
            raise ValueError("Token provided is not a refresh token.")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid refresh token payload.")

        user = await self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User associated with this refresh token is inactive or not found.")

        token_data = {
            "sub": user.user_id,
            "role": user.role,
            "username": user.username
        }

        access_token = JWTManager.create_access_token(token_data)
        new_refresh_token = JWTManager.create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

def get_auth_service() -> AuthService:
    repo = get_user_repository()
    return AuthService(repository=repo)
