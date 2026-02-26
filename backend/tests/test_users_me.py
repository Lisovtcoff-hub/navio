from tests.helpers import signup


def test_me_requires_auth(client, db):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_me_returns_user(client, db):
    tokens = signup(client, db, email="me@example.com", nickname="capy_me")
    access = tokens["access_token"]

    resp = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["nickname"] == "capy_me"
    assert "points" in data
