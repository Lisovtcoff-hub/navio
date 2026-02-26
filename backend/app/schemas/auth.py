from pydantic import BaseModel


class RequestCodeIn(BaseModel):
    identifier: str


class RequestCodeOut(BaseModel):
    masked_email: str


class VerifyCodeIn(BaseModel):
    identifier: str
    code: str
    nickname: str | None = None


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class LogoutOut(BaseModel):
    ok: bool = True
