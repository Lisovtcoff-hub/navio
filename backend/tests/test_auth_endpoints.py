from sqlalchemy import select

from app.core.security import hash_with_pepper
from app.models.refresh_session import RefreshSession
from app.models.user import User
from tests.helpers import login, signup


def test_signup_creates_user_and_returns_tokens(client, db):
    tokens = signup(client, db, email="a@example.com", nickname="capy_a")

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # проверим что пользователь реально создан
    user = db.execute(select(User).where(User.email == "a@example.com")).scalar_one_or_none()
    assert user is not None
    assert user.nickname == "capy_a"


def test_login_existing_user_does_not_require_nickname(client, db):
    # сначала создаём пользователя
    signup(client, db, email="b@example.com", nickname="capy_b")

    # теперь логин без nickname
    tokens = login(client, db, identifier="b@example.com")
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_logout_revokes_current_refresh_session(client, db):
    tokens = signup(client, db, email="c@example.com", nickname="capy_c")
    refresh = tokens["refresh_token"]

    resp = client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    assert resp.status_code == 200, resp.text
    assert resp.json()["ok"] is True

    # Находим именно эту сессию по hash refresh токена
    token_hash = hash_with_pepper(refresh)
    sess = db.execute(
        select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    ).scalar_one()

    assert sess.revoked_at is not None


def test_logout_all_revokes_all_sessions(client, db):
    tokens = signup(client, db, email="d@example.com", nickname="capy_d")
    access = tokens["access_token"]

    # создадим ещё одну сессию (refresh rotation не создаёт новую строку, он обновляет hash)
    # поэтому лучше сделать второй логин -> появится вторая запись refresh_sessions
    # Сидим второй login_code и вызываем verify-code ещё раз (login), чтобы появилась вторая сессия

    # ПРОСТО: ещё раз вызовем signup/login по тому же email (это будет login)
    # (в твоей реализации verify-code для существующего user nickname не нужен)
    from tests.helpers import seed_login_code

    code2 = seed_login_code(db, "d@example.com")
    r_login2 = client.post(
        "/api/v1/auth/verify-code", json={"identifier": "d@example.com", "code": code2}
    )
    assert r_login2.status_code == 200, r_login2.text

    # logout-all
    resp = client.post(
        "/api/v1/auth/logout-all", headers={"Authorization": f"Bearer {access}"}, json={}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ok"] is True

    # Получим user_id по email
    user = db.execute(select(User).where(User.email == "d@example.com")).scalar_one()

    # Проверяем только сессии этого пользователя
    sessions = (
        db.execute(select(RefreshSession).where(RefreshSession.user_id == user.id)).scalars().all()
    )

    assert len(sessions) >= 2
    assert all(s.revoked_at is not None for s in sessions)
