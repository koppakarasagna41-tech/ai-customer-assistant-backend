from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.repositories.user_repository import UserRepository, get_user_repository
from app.security.jwt import JWTManager
from app.security.oauth import oauth2_scheme


async def get_current_user(
    token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = JWTManager.decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise credentials_exception
    except ValueError as exc:
        raise credentials_exception from exc

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return User(**user.dict())
