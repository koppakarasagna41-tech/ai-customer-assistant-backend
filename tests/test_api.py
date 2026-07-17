from fastapi.testclient import TestClient


def test_api_router_health(base_client: TestClient):
    response = base_client.get("/api/v1/health")
    assert response.status_code == 200


def test_api_missing_endpoint(base_client: TestClient):
    response = base_client.get("/api/v1/completely-nonexistent-endpoint-path")
    assert response.status_code == 404


def test_api_invalid_method(base_client: TestClient):
    response = base_client.post("/api/v1/health")
    # Health check is GET only, POST should be rejected (405 Method Not Allowed)
    assert response.status_code == 405


def test_api_unauthorized_user_profile(base_client: TestClient):
    response = base_client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_api_cors_or_common_headers(base_client: TestClient):
    response = base_client.get("/api/v1/health")
    # Ensure standard response format headers are clean
    assert "content-type" in response.headers
    assert "application/json" in response.headers["content-type"]
