from typing import Any, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: str
    username: str
    email: str
    password: str
    user_type: str

class TokenPayload(BaseModel):
    user_id: str
    user_name: str
    email: str
    user_type: str
    exp: int


class AzureActiveDirectoryUserRequest(BaseModel):
    access_token: str
    token_type: Optional[str]
    expires_in: Optional[str]
    scope: Optional[str]
    id_token: Optional[str]
    state: Optional[str]
    session_state: Optional[str]


class SAMLSessionLoginRequest(BaseModel):
    session_key: str


class ResetPasswordRequest(BaseModel):
    userName: str
    key: Optional[Any]
    captcha: Optional[str]
    new_password: Optional[str]
    confirm_password: Optional[str]
    old_password: Optional[str]


class ForgotPasswordRequest(BaseModel):
    userName: Optional[str]
    captcha: Optional[str]
    user_id: Optional[str]


class CaptchaRequest(BaseModel):
    fontSizeMax: Optional[int]
    fontSizeMin: Optional[int]
    height: Optional[int]
    maxLength: Optional[int]
    width: Optional[int]


class ValidateCaptchaRequest(BaseModel):
    captcha: Optional[str]
    user_id: Optional[str]


class RefreshToken(BaseModel):
    user_id: Optional[str]
    project_id: Optional[str]


class SupportLensToken(BaseModel):
    user_id: Optional[str]
    project_id: Optional[str]
    origin: Optional[str]


class GetMongoDetails(BaseModel):
    vkey: str


class VerifyMFA(BaseModel):
    user_id: str
    auth_token: Optional[str]
    tz: Optional[str]


class GcToken(BaseModel):
    user_id: Optional[str]
    project_id: Optional[str]
    age: Optional[int] = 60

