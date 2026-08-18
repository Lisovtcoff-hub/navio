import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException

_DEVELOPMENT_ENVS = {"dev", "development", "local", "test"}


def _load_secret(name: str, development_default: str) -> str:
    value = os.getenv(name, "").strip()
    app_env = os.getenv("APP_ENV", "development").strip().lower()

    if value:
        if app_env not in _DEVELOPMENT_ENVS and len(value) < 32:
            raise RuntimeError(f"{name} must contain at least 32 characters")
        return value

    if app_env in _DEVELOPMENT_ENVS:
        return development_default

    raise RuntimeError(f"{name} must be configured in the environment")


def hash_with_pepper(value: str) -> str:
    pepper = _load_secret(
        "LOGIN_CODE_PEPPER",
        "development-login-code-pepper-change-me",
    )
    data = (pepper + ":" + value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def generate_login_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def utcnow() -> datetime:
    return datetime.now(UTC)


def make_access_token(user_id: str) -> str:
    secret = _load_secret(
        "JWT_SECRET",
        "development-jwt-secret-change-me-now",
    )
    ttl_min = int(os.getenv("JWT_ACCESS_TTL_MIN", "15"))
    payload = {
        "sub": user_id,
        "exp": utcnow() + timedelta(minutes=ttl_min),
        "iat": utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def decode_access_token(token: str) -> str:
    """Validate an access JWT and return its subject user ID."""
    secret = _load_secret(
        "JWT_SECRET",
        "development-jwt-secret-change-me-now",
    )
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail="Access token expired") from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(status_code=401, detail="Invalid access token") from err

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid access token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return str(sub)
