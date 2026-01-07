"""Auth Schemas"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# 请求模型
class RegisterRequest(BaseModel):
    """注册请求"""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """登录请求"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    current_password: str
    new_password: str = Field(min_length=8)


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""

    email: EmailStr


class ResetPasswordConfirmRequest(BaseModel):
    """确认重置密码请求"""

    token: str
    new_password: str = Field(min_length=8)


# 响应模型
class TokenResponse(BaseModel):
    """令牌响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户响应"""

    id: str
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    roles: list[str]
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """认证响应"""

    user: UserResponse
    tokens: TokenResponse
