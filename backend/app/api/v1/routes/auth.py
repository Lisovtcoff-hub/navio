from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    generate_login_code,
    generate_refresh_token,
    hash_with_pepper,
    make_access_token,
    utcnow,
)
from app.deps import get_db
from app.models.login_code import LoginCode
from app.models.refresh_session import RefreshSession
from app.models.user import User
from app.schemas.auth import RefreshIn, RequestCodeIn, TokenPairOut, VerifyCodeIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-code")
def request_code(payload: RequestCodeIn, db: Annotated[Session, Depends(get_db)]):
    ttl = int(__import__("os").getenv("LOGIN_CODE_TTL_MIN", "10"))
    code = generate_login_code()

    row = LoginCode(
        email=str(payload.email).lower(),
        code_hash=hash_with_pepper(code),
        expires_at=utcnow() + timedelta(minutes=ttl),
        attempts_left=5,
    )
    db.add(row)
    db.commit()

    # MVP: вместо email отправки — лог/печать
    print(f"[Navio] login code for {row.email}: {code}")

    return {"ok": True}


@router.post("/verify-code", response_model=TokenPairOut)
def verify_code(payload: VerifyCodeIn, db: Annotated[Session, Depends(get_db)]):
    email = str(payload.email).lower()
    code_hash = hash_with_pepper(payload.code)

    stmt = (
        select(LoginCode)
        .where(LoginCode.email == email)
        .where(LoginCode.consumed_at.is_(None))
        .order_by(LoginCode.created_at.desc())
        .limit(1)
    )
    login_code = db.execute(stmt).scalar_one_or_none()

    if not login_code:
        raise HTTPException(status_code=400, detail="Invalid code")

    if login_code.expires_at < utcnow():
        raise HTTPException(status_code=400, detail="Code expired")

    if login_code.attempts_left <= 0:
        raise HTTPException(status_code=400, detail="Too many attempts")

    if login_code.code_hash != code_hash:
        login_code.attempts_left -= 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid code")

    # consume
    login_code.consumed_at = utcnow()
    db.commit()

    # get or create user
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        user = User(email=email, nickname=email.split("@")[0])
        db.add(user)
        db.commit()
        db.refresh(user)

    access = make_access_token(str(user.id))
    refresh = generate_refresh_token()

    session = RefreshSession(
        user_id=user.id,
        refresh_token_hash=hash_with_pepper(refresh),
        expires_at=utcnow() + timedelta(days=30),
    )
    db.add(session)
    db.commit()

    return TokenPairOut(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPairOut)
def refresh_tokens(payload: RefreshIn, db: Annotated[Session, Depends(get_db)]):
    refresh_token = payload.refresh_token
    token_hash = hash_with_pepper(refresh_token)

    session = db.execute(
        select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    ).scalar_one_or_none()

    if not session or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if session.expires_at < utcnow():
        raise HTTPException(status_code=401, detail="Refresh expired")

    access = make_access_token(str(session.user_id))
    new_refresh = generate_refresh_token()

    session.refresh_token_hash = hash_with_pepper(new_refresh)
    db.commit()

    return TokenPairOut(access_token=access, refresh_token=new_refresh)
