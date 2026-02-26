from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.users import UserMeOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeOut)
def me(user: Annotated[User, Depends(get_current_user)]):
    return UserMeOut(
        id=str(user.id),
        email=user.email,
        nickname=user.nickname,
        is_teacher=user.is_teacher,
        points=user.points,
        created_at=user.created_at,
    )
