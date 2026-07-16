import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.models.user import User, UserInDB
from app.security.password import PasswordHasher
from app.security.permissions import ROLE_PERMISSIONS

class UserRepository:
    def __init__(self):
        self._users: Dict[str, UserInDB] = {}
        self._lock = asyncio.Lock()
        self._seed_data()

    def _seed_data(self):
        # Seed some enterprise users for testing
        now = datetime.now(timezone.utc)
        
        roles_and_users = [
            ("customer_user", "customer@enterprise.com", "customer", "Customer User", "cust_pass123"),
            ("support_agent_user", "agent@enterprise.com", "support_agent", "Support Agent User", "agent_pass123"),
            ("support_admin_user", "admin@enterprise.com", "support_admin", "Support Admin User", "admin_pass123"),
            ("supervisor_user", "supervisor@enterprise.com", "supervisor", "Supervisor User", "super_pass123"),
            ("system_admin_user", "sysadmin@enterprise.com", "system_admin", "System Admin User", "sysadmin_pass123")
        ]

        for username, email, role, full_name, password in roles_and_users:
            user_id = f"USR-{hash(username) % 100000:05d}"
            hashed = PasswordHasher.hash_password(password)
            perms = [p.value for p in ROLE_PERMISSIONS.get(role, [])]
            
            self._users[user_id] = UserInDB(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                is_active=True,
                created_at=now,
                updated_at=now,
                permissions=perms,
                hashed_password=hashed
            )

    async def create(self, user: UserInDB) -> UserInDB:
        async with self._lock:
            self._users[user.user_id] = user
            return user

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        async with self._lock:
            return self._users.get(user_id)

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        async with self._lock:
            for user in self._users.values():
                if user.username.lower() == username.lower():
                    return user
            return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        async with self._lock:
            for user in self._users.values():
                if user.email.lower() == email.lower():
                    return user
            return None

    async def list_users(self) -> List[UserInDB]:
        async with self._lock:
            return list(self._users.values())

# Shared global repository instance for in-memory storage
_user_repo_instance = UserRepository()

def get_user_repository() -> UserRepository:
    return _user_repo_instance
