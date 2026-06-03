"""
Test — Auth endpoints.
"""


def test_register_and_login(client, auth_headers):
    """Test admin-created user registration then login flow."""
    # Register
    resp = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@crm.local",
        "password": "test1234",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@crm.local"
    assert data["role"] == "commercial"

    # Login
    resp = client.post("/api/v1/auth/login", json={
        "email": "test@crm.local",
        "password": "test1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@crm.local"


def test_login_wrong_password(client, auth_headers):
    # Register first
    client.post("/api/v1/auth/register", json={
        "name": "Temp User",
        "email": "temp@crm.local",
        "password": "correctpass",
    }, headers=auth_headers)
    # Try wrong password
    resp = client.post("/api/v1/auth/login", json={
        "email": "temp@crm.local",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_get_me(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "testadmin@crm.local"


def test_non_admin_cannot_read_another_user_profile(client, auth_headers):
    register = client.post("/api/v1/auth/register", json={
        "name": "Limited User",
        "email": "limited@crm.local",
        "password": "limited123",
    }, headers=auth_headers)
    assert register.status_code == 201

    login = client.post("/api/v1/auth/login", json={
        "email": "limited@crm.local",
        "password": "limited123",
    })
    assert login.status_code == 200
    limited_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    admin_me = client.get("/api/v1/auth/me", headers=auth_headers)
    admin_id = admin_me.json()["id"]

    resp = client.get(f"/api/v1/users/{admin_id}", headers=limited_headers)
    assert resp.status_code == 403


def test_protected_route_without_token(client):
    resp = client.get("/api/v1/accounts")
    assert resp.status_code == 401
