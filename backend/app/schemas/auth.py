from pydantic import BaseModel, EmailStr


class RequestCodeIn(BaseModel):
    email: EmailStr


class VerifyCodeIn(BaseModel):
    email: EmailStr
    code: str


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshIn(BaseModel):
    refresh_token: str
