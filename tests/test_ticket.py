from fastapi.testclient import TestClient


def test_classify_ticket_billing(base_client: TestClient):
    payload = {
        "title": "Need help",
        "description": "My credit card was charged twice for the latest monthly invoice.",
        "category": "technical",
        "priority": "low",
    }
    response = base_client.post("/api/v1/tickets/classify", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["category"] == "billing"
    assert res_data["data"]["priority"] == "high"


def test_create_ticket(base_client: TestClient):
    payload = {
        "title": "SSO integration fail",
        "description": "We are getting a login timeout from Okta.",
        "category": "technical",
        "priority": "urgent",
    }
    response = base_client.post("/api/v1/tickets/create", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["ticket_id"].startswith("TCK-")
    assert res_data["data"]["title"] == "SSO integration fail"


def test_list_tickets_with_filters(base_client: TestClient):
    # Retrieve billing tickets only
    response = base_client.get("/api/v1/tickets?category=billing")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    items = res_data["data"]["items"]
    assert len(items) > 0
    for item in items:
        assert item["category"] == "billing"


def test_get_ticket_details(base_client: TestClient):
    response = base_client.get("/api/v1/tickets/TCK-10001")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["ticket_id"] == "TCK-10001"
    assert len(res_data["data"]["timeline"]) > 0


def test_get_ticket_not_found(base_client: TestClient):
    response = base_client.get("/api/v1/tickets/TCK-99999")
    assert response.status_code == 404


def test_update_ticket(base_client: TestClient):
    payload = {
        "title": "New title for SSO Okta issue",
        "description": "Updated ticket description regarding SSO Okta authentication.",
    }
    response = base_client.patch("/api/v1/tickets/TCK-10002", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["title"] == "New title for SSO Okta issue"


def test_update_status(base_client: TestClient):
    payload = {"status": "closed"}
    response = base_client.post("/api/v1/tickets/TCK-10001/status", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "closed"


def test_update_priority(base_client: TestClient):
    payload = {"priority": "low"}
    response = base_client.post("/api/v1/tickets/TCK-10001/priority", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["priority"] == "low"


def test_assign_agent(base_client: TestClient):
    payload = {"assigned_agent_id": "AGT-999"}
    response = base_client.post("/api/v1/tickets/TCK-10001/assign", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["assigned_agent_id"] == "AGT-999"


def test_add_comment(base_client: TestClient):
    payload = {"author": "customer", "content": "This is a test comment by customer"}
    response = base_client.post("/api/v1/tickets/TCK-10001/comments", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["content"] == "This is a test comment by customer"


def test_delete_ticket(base_client: TestClient):
    response = base_client.delete("/api/v1/tickets/TCK-10003")
    assert response.status_code == 200
    assert response.json()["data"] is True
