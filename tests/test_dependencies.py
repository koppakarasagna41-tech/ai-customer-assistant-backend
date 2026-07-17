import pytest
from fastapi import HTTPException

from app.dependencies.current_user import PermissionChecker, RoleChecker
from app.models.user import User
from app.security.permissions import Permission


# Mock simple User model
@pytest.fixture
def mock_user() -> User:
    return User(
        user_id="USR-123",
        username="test_user",
        email="test_user@enterprise.com",
        full_name="Test User",
        role="customer",
        is_active=True,
        permissions=["create_ticket", "access_ai_chat"],
    )


def test_role_checker_success(mock_user: User):
    checker = RoleChecker(allowed_roles=["customer", "support_agent"])
    checked_user = checker(current_user=mock_user)
    assert checked_user == mock_user


def test_role_checker_forbidden(mock_user: User):
    checker = RoleChecker(allowed_roles=["support_admin"])
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=mock_user)
    assert exc_info.value.status_code == 403


def test_permission_checker_success(mock_user: User):
    checker = PermissionChecker(required_permission=Permission.CREATE_TICKET)
    checked_user = checker(current_user=mock_user)
    assert checked_user == mock_user


def test_permission_checker_forbidden(mock_user: User):
    checker = PermissionChecker(required_permission=Permission.MANAGE_USERS)
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=mock_user)
    assert exc_info.value.status_code == 403
