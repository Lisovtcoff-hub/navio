import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.deps.db import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    # 1) Проверяем, что Authorization: Bearer ... вообще пришёл
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = creds.credentials

    # 2) Декодируем JWT и получаем sub = user_id
    sub = decode_access_token(token)

    # 3) sub должен быть UUID
    try:
        user_id = uuid.UUID(sub)
    except ValueError as err:
        raise HTTPException(status_code=401, detail="Invalid access token") from err

    # 4) Ищем пользователя в БД
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
