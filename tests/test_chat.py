import pytest
from fastapi.testclient import TestClient

def test_chat_success(customer_client: TestClient):
    payload = {
        "message": "Hello, I am having issues with my account billing.",
        "context": {
            "user_id": "USR-12345",
            "session_id": "session-abc-123",
            "metadata": {
                "browser": "chrome",
                "ip_address": "127.0.0.1"
            }
        }
    }
    response = customer_client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["message"] == "Chat processed successfully"
    
    data = res_data["data"]
    assert "response" in data
    assert data["intent"] == "SUPPORT_QUERY"
    assert data["metadata"]["sentiment"] == "neutral"
    assert data["metadata"]["category"] == "technical"
    assert "token_usage" in data["metadata"]

def test_chat_empty_message(customer_client: TestClient):
    payload = {
        "message": "   "
    }
    response = customer_client.post("/api/v1/chat", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
