import asyncio
from contextlib import suppress
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.db_models.user import User as DBUser
from app.models.user import UserInDB
from app.security.password import PasswordHasher


class UserRepository:
    def __init__(self):
        self.db: Session = SessionLocal()
        self._lock = asyncio.Lock()
        self._users: dict[str, UserInDB] = {}
        self._seed_data()

    def __del__(self):
        """Close database session when repository is destroyed."""
        if hasattr(self, "db") and self.db:
            with suppress(Exception):
                self.db.close()
                

    def _seed_data(self) -> None:
        if self._users:
            return

        now = datetime.now(UTC)
        self._users = {
            "USR-10001": UserInDB(
                user_id="USR-10001",
                username="customer_user",
                email="customer@enterprise.com",
                full_name="Customer User",
                hashed_password=PasswordHasher.hash_password("cust_pass123"),
                role="customer",
                permissions=["create_ticket", "update_ticket", "access_ai_chat"],
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
            "USR-10002": UserInDB(
                user_id="USR-10002",
                username="support_agent_user",
                email="agent@enterprise.com",
                full_name="Support Agent User",
                hashed_password=PasswordHasher.hash_password("agent_pass123"),
                role="support_agent",
                permissions=["create_ticket", "update_ticket", "assign_ticket", "access_ai_chat"],
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
            "USR-10003": UserInDB(
                user_id="USR-10003",
                username="support_admin_user",
                email="admin@enterprise.com",
                full_name="Support Admin User",
                hashed_password=PasswordHasher.hash_password("admin_pass123"),
                role="support_admin",
                permissions=[
                    "create_ticket",
                    "update_ticket",
                    "assign_ticket",
                    "access_ai_chat",
                    "manage_knowledge_base",
                ],
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
            "USR-10004": UserInDB(
                user_id="USR-10004",
                username="supervisor_user",
                email="supervisor@enterprise.com",
                full_name="Supervisor User",
                hashed_password=PasswordHasher.hash_password("super_pass123"),
                role="supervisor",
                permissions=[
                    "create_ticket",
                    "update_ticket",
                    "assign_ticket",
                    "access_ai_chat",
                    "view_analytics",
                    "export_reports",
                    "manage_knowledge_base",
                ],
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
            "USR-10005": UserInDB(
                user_id="USR-10005",
                username="system_admin_user",
                email="sysadmin@enterprise.com",
                full_name="System Admin User",
                hashed_password=PasswordHasher.hash_password("sysadmin_pass123"),
                role="system_admin",
                permissions=[
                    "create_ticket",
                    "update_ticket",
                    "delete_ticket",
                    "assign_ticket",
                    "view_analytics",
                    "export_reports",
                    "access_ai_chat",
                    "manage_knowledge_base",
                    "manage_users",
                ],
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
        }

    async def create(self, user: UserInDB) -> UserInDB:
        self._users[user.user_id] = user
        try:
            db_user = DBUser(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                role=user.role,
                permissions=user.permissions,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except Exception:
            self.db.rollback()

        return user

    async def get_by_id(self, user_id: str) -> UserInDB | None:
        if user_id in self._users:
            return self._users[user_id]

        if self._users:
            return None

        db_user = self.db.query(DBUser).filter(DBUser.user_id == user_id).first()

        if not db_user:
            return None

        user = UserInDB(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            hashed_password=db_user.hashed_password,
            role=db_user.role,
            permissions=db_user.permissions,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
        self._users[user.user_id] = user
        return user

    async def get_by_username(self, username: str) -> UserInDB | None:
        for user in self._users.values():
            if user.username == username:
                return user

        if self._users:
            return None

        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()

        if not db_user:
            return None

        user = UserInDB(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            hashed_password=db_user.hashed_password,
            role=db_user.role,
            permissions=db_user.permissions,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
        self._users[user.user_id] = user
        return user

    async def get_by_email(self, email: str) -> UserInDB | None:
        for user in self._users.values():
            if user.email == email:
                return user

        if self._users:
            return None

        db_user = self.db.query(DBUser).filter(DBUser.email == email).first()

        if not db_user:
            return None

        user = UserInDB(
            user_id=db_user.user_id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            hashed_password=db_user.hashed_password,
            role=db_user.role,
            permissions=db_user.permissions,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
        self._users[user.user_id] = user
        return user

    async def list_users(self) -> list[UserInDB]:
        if self._users:
            return list(self._users.values())

        db_users = self.db.query(DBUser).all()

        return [
            UserInDB(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                role=user.role,
                permissions=user.permissions,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in db_users
        ]

    async def update(self, user_id: str, **kwargs) -> UserInDB | None:
        user = self._users.get(user_id)
        if user is None:
            user = await self.get_by_id(user_id)
        if user is None:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.now(UTC)
        self._users[user.user_id] = user

        db_user = self.db.query(DBUser).filter(DBUser.user_id == user_id).first()
        if db_user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(db_user, key, value)
            db_user.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(db_user)

        return user

    async def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            self._users.pop(user_id, None)

        db_user = self.db.query(DBUser).filter(DBUser.user_id == user_id).first()

        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True


_user_repo_instance = UserRepository()


def get_user_repository():
    return _user_repo_instance
