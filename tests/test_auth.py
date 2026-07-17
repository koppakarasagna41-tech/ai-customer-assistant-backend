from fastapi.testclient import TestClient


def test_register_user_success(base_client: TestClient):
    payload = {
        "username": "new_customer_99",
        "email": "new_cust99@enterprise.com",
        "password": "strongpassword123",
        "full_name": "John Doe Customer",
        "role": "customer",
    }
    response = base_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["message"] == "User registered successfully"
    assert "user_id" in res_data["data"]
    assert res_data["data"]["username"] == "new_customer_99"
    assert res_data["data"]["role"] == "customer"


def test_register_duplicate_username(base_client: TestClient):
    payload = {
        "username": "customer_user",  # already seeded
        "email": "diff_email@enterprise.com",
        "password": "some_password",
        "full_name": "Another Name",
        "role": "customer",
    }
    response = base_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_register_duplicate_email(base_client: TestClient):
    payload = {
        "username": "diff_username",
        "email": "customer@enterprise.com",  # already seeded
        "password": "some_password",
        "full_name": "Another Name",
        "role": "customer",
    }
    response = base_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_invalid_role(base_client: TestClient):
    payload = {
        "username": "invalid_role_user",
        "email": "invalid_role@enterprise.com",
        "password": "some_password",
        "full_name": "Invalid Role",
        "role": "super-hacker-role",
    }
    response = base_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]


def test_login_success(base_client: TestClient):
    payload = {"username_or_email": "customer_user", "password": "cust_pass123"}
    response = base_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "access_token" in res_data["data"]
    assert "refresh_token" in res_data["data"]
    assert res_data["data"]["token_type"] == "bearer"


def test_login_invalid_password(base_client: TestClient):
    payload = {"username_or_email": "customer_user", "password": "wrong_password"}
    response = base_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid username" in response.json()["detail"]


def test_token_refresh(base_client: TestClient):
    # Log in first
    login_payload = {"username_or_email": "customer_user", "password": "cust_pass123"}
    login_res = base_client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["data"]["refresh_token"]

    # Request fresh access token
    refresh_payload = {"refresh_token": refresh_token}
    refresh_res = base_client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert refresh_res.status_code == 200
    res_data = refresh_res.json()
    assert res_data["success"] is True
    assert "access_token" in res_data["data"]


def test_token_refresh_invalid(base_client: TestClient):
    refresh_payload = {"refresh_token": "completely_fake_refresh_token"}
    refresh_res = base_client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert refresh_res.status_code == 401


def test_get_me_unauthorized(base_client: TestClient):
    response = base_client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_authorized(customer_client: TestClient):
    response = customer_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["username"] == "customer_user"
    assert res_data["data"]["role"] == "customer"


def test_logout(customer_client: TestClient):
    response = customer_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
