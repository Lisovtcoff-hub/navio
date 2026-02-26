from datetime import timedelta

from app.core.security import generate_login_code, hash_with_pepper, utcnow
from app.models.login_code import LoginCode


def test_auth_verify_and_refresh(client, db):
    email = "test@example.com"
    code = generate_login_code()

    # имитируем request-code: кладём login_code в БД
    row = LoginCode(
        email=email,
        code_hash=hash_with_pepper(code),
        expires_at=utcnow() + timedelta(minutes=10),
        attempts_left=5,
    )
    db.add(row)
    db.commit()

    # verify-code (signup, потому что user ещё не создан)
    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email, "code": code, "nickname": "capy_test"},
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    refresh = data["refresh_token"]

    # refresh -> rotation: получаем новый refresh
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 200, r2.text

    data2 = r2.json()
    assert "access_token" in data2
    assert "refresh_token" in data2
    assert data2["refresh_token"] != refresh  # rotation
