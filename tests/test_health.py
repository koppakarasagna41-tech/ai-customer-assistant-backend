from fastapi.testclient import TestClient

def test_get_health(base_client: TestClient):
    response = base_client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Service is healthy"
    
    data = json_data["data"]
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert data["services"]["database"] == "connected"
    assert data["services"]["ai_gateway"] == "online"
    assert data["services"]["retriever"] == "online"
