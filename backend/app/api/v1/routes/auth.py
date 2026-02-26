import re
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    generate_login_code,
    generate_refresh_token,
    hash_with_pepper,
    make_access_token,
    utcnow,
)
from app.deps import get_current_user, get_db
from app.models.login_code import LoginCode
from app.models.refresh_session import RefreshSession
from app.models.user import User
from app.schemas.auth import (
    LogoutIn,
    LogoutOut,
    RefreshIn,
    RequestCodeIn,
    RequestCodeOut,
    TokenPairOut,
    VerifyCodeIn,
)
from app.services.emailer import send_login_code

NICK_RE = re.compile(r"^[a-z0-9_]{3,24}$")


def normalize_and_validate_nickname(raw: str | None) -> str | None:
    if raw is None:
        return None
    nick = raw.strip().lower()
    if not NICK_RE.match(nick):
        return None
    return nick


def mask_email(email: str) -> str:
    name, _, domain = email.partition("@")
    if not domain:
        return "***"
    if len(name) <= 1:
        return "*@" + domain
    return name[0] + "***@" + domain


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-code", response_model=RequestCodeOut)
def request_code(
    payload: RequestCodeIn,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
):
    ident = payload.identifier.strip()
    if not ident:
        raise HTTPException(status_code=400, detail="Identifier required")

    target_email: str | None = None

    if "@" in ident:
        # email
        target_email = ident.lower()
    else:
        # nickname -> find user -> email
        nick = normalize_and_validate_nickname(ident)
        if nick:
            user = db.execute(select(User).where(User.nickname == nick)).scalar_one_or_none()
            if user:
                target_email = user.email

    # anti-enumeration: одинаковый ответ
    if not target_email:
        # не говорим “нет такого пользователя”
        return RequestCodeOut(masked_email="***")

    # дальше твой текущий код: генерим код, хешируем, кладём в LoginCode
    code = generate_login_code()  # как у тебя сейчас
    code_hash = hash_with_pepper(code)

    login_code = LoginCode(
        email=target_email,
        code_hash=code_hash,
        expires_at=utcnow() + timedelta(minutes=10),
        attempts_left=5,
    )
    db.add(login_code)
    db.commit()

    # DEV-лог можно оставить временно, но лучше потом выключить флагом
    print(f"[login code] {target_email}: {code}")

    # Важно: отправку делаем после commit, чтобы код точно был сохранён
    try:
        background_tasks.add_task(send_login_code, target_email, code)
    except Exception:
        # если не отправилось — не критично, код всё равно сохранён
        print(f"[login code] failed to send email to {target_email}")
    return RequestCodeOut(masked_email=mask_email(target_email))


@router.post("/verify-code", response_model=TokenPairOut)
def verify_code(payload: VerifyCodeIn, db: Annotated[Session, Depends(get_db)]):
    ident = payload.identifier.strip()
    if not ident:
        raise HTTPException(status_code=400, detail="Invalid code")  # одинаковая ошибка

    email: str | None = None

    if "@" in ident:
        email = ident.lower()
    else:
        nick = normalize_and_validate_nickname(ident)
        if nick:
            user_by_nick = db.execute(
                select(User).where(User.nickname == nick)
            ).scalar_one_or_none()
            if user_by_nick:
                email = user_by_nick.email

    # anti-enumeration: если по нику не нашли email — делаем вид, что код “просто неправильный”
    if not email:
        raise HTTPException(status_code=400, detail="Invalid code")

    code_hash = hash_with_pepper(payload.code)

    stmt = (
        select(LoginCode)
        .where(LoginCode.email == email)
        .where(LoginCode.consumed_at.is_(None))  # еще не исползованный
        .order_by(LoginCode.created_at.desc())  # самая свежая запись
        .limit(1)  # самая первая запись после сотрировки
    )
    login_code = db.execute(stmt).scalar_one_or_none()

    if not login_code:
        raise HTTPException(status_code=400, detail="Invalid code")

    if login_code.expires_at < utcnow():
        raise HTTPException(status_code=400, detail="Code expired")

    if login_code.attempts_left <= 0:
        raise HTTPException(status_code=400, detail="Too many attempts")

    # неверный код → уменьшаем attempts_left и фиксируем это сразу
    if login_code.code_hash != code_hash:
        login_code.attempts_left -= 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid code")

    # код верный: дальше НЕ коммитим, пока не убедимся, что всё прошло
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if not user:
        nickname = normalize_and_validate_nickname(payload.nickname)
        if not nickname:
            # код остаётся не consumed → пользователь может повторить с тем же кодом
            raise HTTPException(
                status_code=400,
                detail="Nickname required for new user (3-24 chars: a-z, 0-9, underscore)",
            )

        user = User(email=email, nickname=nickname)
        db.add(user)

        # важно: flush, чтобы получить user.id до создания refresh session
        try:
            db.flush()  # отправляет INSERT в БД, но НЕ commit
        except IntegrityError as err:
            db.rollback()
            # nickname/email заняты — пользователь может попробовать другой ник,
            # а код мы НЕ сожгли (это важно)
            raise HTTPException(status_code=409, detail="Nickname already taken") from err

    # создаём refresh session (user.id уже есть: либо был, либо появился после flush)
    refresh = generate_refresh_token()
    session = RefreshSession(
        user_id=user.id,
        refresh_token_hash=hash_with_pepper(refresh),
        expires_at=utcnow() + timedelta(days=30),
    )
    db.add(session)

    # consume код ТОЛЬКО в самом конце
    login_code.consumed_at = utcnow()

    # один общий commit
    db.commit()

    access = make_access_token(str(user.id))
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


@router.post("/logout", response_model=LogoutOut)
def logout(payload: LogoutIn, db: Annotated[Session, Depends(get_db)]):
    token_hash = hash_with_pepper(payload.refresh_token)

    session = db.execute(
        select(RefreshSession).where(RefreshSession.refresh_token_hash == token_hash)
    ).scalar_one_or_none()

    # Важно: одинаковый ответ, даже если токен невалидный
    # чтобы не палить ничего наружу и чтобы logout был идемпотентным
    if not session or session.revoked_at is not None:
        return LogoutOut(ok=True)

    session.revoked_at = utcnow()
    db.commit()
    return LogoutOut(ok=True)


@router.post("/logout-all", response_model=LogoutOut)
def logout_all(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    # UPDATE refresh_sessions SET revoked_at = now()
    # WHERE user_id = :user_id AND revoked_at IS NULL
    stmt = (
        update(RefreshSession)
        .where(RefreshSession.user_id == user.id)
        .where(RefreshSession.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    db.execute(stmt)
    db.commit()
    return LogoutOut(ok=True)
