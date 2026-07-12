"""Auth: registration, login, and the JWT-protected /auth/me endpoint."""


def test_register_returns_the_new_user(client):
    res = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "password123", "full_name": "New User"},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["email"] == "new@example.com"
    assert body["full_name"] == "New User"
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email_conflicts(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    res = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert res.status_code == 409


def test_login_success_returns_a_token(client):
    client.post("/auth/register", json={"email": "log@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "log@example.com", "password": "password123"})
    assert res.status_code == 200, res.text
    assert res.json()["access_token"]


def test_login_wrong_password_is_rejected(client):
    client.post("/auth/register", json={"email": "wp@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong-password"})
    assert res.status_code == 401


def test_me_requires_a_token(client):
    res = client.get("/auth/me")
    # HTTPBearer rejects a missing Authorization header before our code runs.
    assert res.status_code in (401, 403)


def test_me_returns_the_current_user(client, login_as):
    headers = login_as("me@example.com")
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["email"] == "me@example.com"
