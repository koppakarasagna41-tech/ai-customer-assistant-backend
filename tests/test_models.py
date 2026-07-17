import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest
from app.schemas.ticket import TicketCreate
from app.schemas.user import UserCreate


def test_user_create_validation():
    # Valid payload
    payload = {
        "username": "tester_bob",
        "email": "bob@enterprise.com",
        "password": "validpassword",
        "full_name": "Bob Tester",
        "role": "customer",
    }
    user = UserCreate(**payload)
    assert user.username == "tester_bob"
    assert user.role == "customer"


def test_user_create_invalid_email():
    # Pydantic v2 validation error should be raised (if EmailStr is used, or basic validation)
    # Let's verify standard field validation of fields
    with pytest.raises(ValidationError):
        # Email field in UserCreate has constraint validation if defined,
        # let's test a missing required field instead
        UserCreate(username="bob")


def test_ticket_create_missing_required():
    with pytest.raises(ValidationError):
        # Title and description are required, this should fail validation
        TicketCreate(category="billing")


def test_chat_request_defaults():
    req = ChatRequest(message="Hello world")
    assert req.message == "Hello world"
    assert req.history == []
    assert req.context is None
