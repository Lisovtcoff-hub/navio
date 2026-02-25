from datetime import timedelta

from sqlalchemy import select

from app.core.security import generate_login_code, hash_with_pepper, utcnow
from app.models.login_code import LoginCode
from app.models.refresh_session import RefreshSession


def test_auth_verify_and_refresh(client, db):
    email = "test@example.com"
    code = generate_login_code()

    # Создаём login_code напрямую в БД (имитация request-code)
    row = LoginCode(
        email=email,
        code_hash=hash_with_pepper(code),
        expires_at=utcnow() + timedelta(minutes=10),
        attempts_left=5,
    )
    db.add(row)
    db.commit()

    # verify-code
    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"email": email, "code": code},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    refresh_token = data["refresh_token"]

    # Проверим, что refresh session реально появилась
    token_hash = hash_with_pepper(refresh_token)
    session = db.execute(
        select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    ).scalar_one_or_none()
    assert session is not None

    # refresh
    resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "access_token" in data2
    assert "refresh_token" in data2
    assert data2["refresh_token"] != refresh_token
