import pytest
from fastapi.testclient import TestClient
from app.security.permissions import Permission, ROLE_PERMISSIONS

def test_customer_permissions(customer_client: TestClient):
    response = customer_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    permissions = response.json()["data"]["permissions"]
    
    # Customer should have create_ticket and access_ai_chat but NOT view_analytics or manage_users
    assert "create_ticket" in permissions
    assert "access_ai_chat" in permissions
    assert "view_analytics" not in permissions
    assert "manage_users" not in permissions

def test_agent_permissions(agent_client: TestClient):
    response = agent_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    permissions = response.json()["data"]["permissions"]
    
    assert "create_ticket" in permissions
    assert "assign_ticket" in permissions
    assert "manage_users" not in permissions

def test_sysadmin_permissions(sysadmin_client: TestClient):
    response = sysadmin_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    permissions = response.json()["data"]["permissions"]
    
    assert "manage_users" in permissions
    assert "delete_ticket" in permissions
    assert "view_analytics" in permissions
