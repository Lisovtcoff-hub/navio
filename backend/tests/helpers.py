from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.security import generate_login_code, hash_with_pepper, utcnow
from app.models.login_code import LoginCode


def seed_login_code(db: Session, email: str, code: str | None = None) -> str:
    """
    Имитирует request-code: кладём login_codes запись напрямую.
    Возвращает код (если не передали — сгенерит).
    """
    if code is None:
        code = generate_login_code()

    row = LoginCode(
        email=email,
        code_hash=hash_with_pepper(code),
        expires_at=utcnow() + timedelta(minutes=10),
        attempts_left=5,
    )
    db.add(row)
    db.commit()
    return code


def signup(client, db, email: str, nickname: str):
    """
    Делает signup: создаёт login_code и вызывает verify-code.
    Возвращает dict с токенами.
    """
    code = seed_login_code(db, email)
    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email, "code": code, "nickname": nickname},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def login(client, db, identifier: str, target_email: str | None = None):
    """
    Делает login:
    - если identifier = email → target_email можно не передавать
    - если identifier = nickname → target_email = email пользователя (код хранится по email)
      Но в реальном мире request-code сам найдёт email. В тестах проще:
      - сидим login_code в БД под реальный email
      - verify-code вызываем с identifier (nickname или email)
    """
    if target_email is None:
        target_email = identifier

    code = seed_login_code(db, target_email)
    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": identifier, "code": code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def seed_login_code_custom(
    db: Session,
    email: str,
    code: str,
    expires_in_seconds: int = 600,
    attempts_left: int = 5,
) -> None:
    row = LoginCode(
        email=email,
        code_hash=hash_with_pepper(code),
        expires_at=utcnow() + timedelta(seconds=expires_in_seconds),
        attempts_left=attempts_left,
    )
    db.add(row)
    db.commit()
