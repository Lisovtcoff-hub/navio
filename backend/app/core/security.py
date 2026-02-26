import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException


def hash_with_pepper(value: str) -> str:
    pepper = os.getenv("LOGIN_CODE_PEPPER", "dev-pepper")
    data = (pepper + ":" + value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def generate_login_code() -> str:
    # 6-значный код (000000..999999)
    return f"{secrets.randbelow(1_000_000):06d}"


def utcnow() -> datetime:
    return datetime.now(UTC)


def make_access_token(user_id: str) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret")
    ttl_min = int(os.getenv("JWT_ACCESS_TTL_MIN", "15"))
    payload = {
        "sub": user_id,
        "exp": utcnow() + timedelta(minutes=ttl_min),
        "iat": utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def generate_refresh_token() -> str:
    # длинный случайный токен
    return secrets.token_urlsafe(48)


def decode_access_token(token: str) -> str:
    """
    Проверяет access JWT:
    - подпись (JWT_SECRET)
    - exp (PyJWT проверяет автоматически)
    - type == "access"
    Возвращает user_id (sub) строкой.
    """
    secret = os.getenv("JWT_SECRET", "dev-secret")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as err:
        # exp истёк
        raise HTTPException(status_code=401, detail="Access token expired") from err
    except jwt.InvalidTokenError as err:
        # подпись не сошлась / токен битый / не тот формат
        raise HTTPException(status_code=401, detail="Invalid access token") from err

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid access token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return str(sub)
