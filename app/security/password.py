from typing import cast

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return cast(str, pwd_context.hash(password))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return cast(bool, pwd_context.verify(plain_password, hashed_password))
        except Exception:
            return False
