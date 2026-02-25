import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt


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
