from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.security.permissions import Permission


# Reusable role validator
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.lower() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}",
            )
        return current_user


# Reusable permission validator
class PermissionChecker:
    def __init__(self, required_permission: Permission):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if self.required_permission.value not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Operation not permitted. Missing required permission: "
                    f"{self.required_permission.value}"
                ),
            )
        return current_user
