import os
import sys
from collections.abc import Generator

import pytest

# Ensure the app directory is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set environment variables for testing
os.environ["GEMINI_API_KEY"] = "mock-gemini-api-key-for-testing"
os.environ["JWT_SECRET"] = "mock-jwt-secret-key-for-testing-purposes-123"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.router import api_router
from app.repositories.ticket_repository import get_ticket_repository
from app.repositories.user_repository import get_user_repository
from app.services.gemini_client import GeminiClient
from app.services.vector_store import VectorStoreFactory


# Create a clean test FastAPI application
@pytest.fixture(scope="session")
def app() -> FastAPI:
    VectorStoreFactory.set_provider("in_memory")
    application = FastAPI(title="Enterprise AI Support - Test Workspace")
    application.include_router(api_router, prefix="/api/v1")
    return application


# Base HTTP client
@pytest.fixture(scope="session")
def base_client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


# Helper to log in and return a client with auth headers
def get_authenticated_client(base_client: TestClient, username: str, password: str) -> TestClient:
    login_payload = {"username_or_email": username, "password": password}
    response = base_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200, f"Login failed for {username}: {response.text}"
    token_data = response.json()["data"]["access_token"]

    # Create a new client or clone with Authorization headers set
    authenticated_client = TestClient(base_client.app)
    authenticated_client.headers.update({"Authorization": f"Bearer {token_data}"})
    return authenticated_client


@pytest.fixture(scope="session")
def customer_client(base_client: TestClient) -> TestClient:
    return get_authenticated_client(base_client, "customer_user", "cust_pass123")


@pytest.fixture(scope="session")
def agent_client(base_client: TestClient) -> TestClient:
    return get_authenticated_client(base_client, "support_agent_user", "agent_pass123")


@pytest.fixture(scope="session")
def admin_client(base_client: TestClient) -> TestClient:
    return get_authenticated_client(base_client, "support_admin_user", "admin_pass123")


@pytest.fixture(scope="session")
def supervisor_client(base_client: TestClient) -> TestClient:
    return get_authenticated_client(base_client, "supervisor_user", "super_pass123")


@pytest.fixture(scope="session")
def sysadmin_client(base_client: TestClient) -> TestClient:
    return get_authenticated_client(base_client, "system_admin_user", "sysadmin_pass123")


# Mocked Gemini API response structure
@pytest.fixture(autouse=True)
def mock_gemini_client(monkeypatch) -> None:
    async def mock_generate_content(
        self,
        contents: list,
        system_instruction: str | None = None,
        response_schema: dict | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1500,
        response_mime_type: str = "text/plain",
    ) -> dict:
        # Default mock structure returning valid JSON
        mock_response = {
            "response": (
                "Thank you for contacting customer support. We are looking into " "your query."
            ),
            "intent": "SUPPORT_QUERY",
            "sentiment": "neutral",
            "category": "technical",
            "urgency": "medium",
            "confidence": 0.92,
            "escalated": False,
            "reason": "Standard user support question without risk signals.",
        }

        # If application/json is requested, return JSON encoded string as output
        if response_mime_type == "application/json":
            text_content = json.dumps(mock_response)
        else:
            text_content = "This is a mock text response from Gemini."

        return {
            "candidates": [
                {"content": {"parts": [{"text": text_content}]}, "finishReason": "STOP"}
            ],
            "usageMetadata": {
                "promptTokenCount": 120,
                "candidatesTokenCount": 85,
                "totalTokenCount": 205,
            },
        }

    # Mock json import inside generator to avoid scope issues
    import json

    monkeypatch.setattr(GeminiClient, "generate_content", mock_generate_content)


# Clean/reset repositories before each test
@pytest.fixture(autouse=True)
async def reset_repositories():
    user_repo = get_user_repository()
    # Re-seed users
    async with user_repo._lock:
        user_repo._users.clear()
    user_repo._seed_data()

    ticket_repo = get_ticket_repository()
    # Re-seed tickets
    async with ticket_repo._lock:
        ticket_repo._tickets.clear()
    ticket_repo._seed_data()
