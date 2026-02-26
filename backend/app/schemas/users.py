from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserMeOut(BaseModel):
    id: str
    email: EmailStr
    nickname: str
    is_teacher: bool
    points: int
    created_at: datetime
