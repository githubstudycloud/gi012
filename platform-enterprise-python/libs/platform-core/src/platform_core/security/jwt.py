"""JWT Token Utilities"""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from platform_core.exceptions import UnauthorizedError


class TokenPayload(BaseModel):
    """Token 载荷"""

    sub: str  # 主题 (通常是用户 ID)
    exp: int  # 过期时间
    iat: int  # 签发时间
    type: str  # 令牌类型: access 或 refresh
    jti: str | None = None  # JWT ID
    email: str | None = None
    roles: list[str] | None = None


class JWTHandler:
    """JWT 处理器"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        subject: str,
        additional_claims: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """创建访问令牌"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)

        expire = datetime.utcnow() + expires_delta
        now = datetime.utcnow()

        payload = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "access",
            **(additional_claims or {}),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        subject: str,
        jti: str | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """创建刷新令牌"""
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)

        expire = datetime.utcnow() + expires_delta
        now = datetime.utcnow()

        payload = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "refresh",
            "jti": jti,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        """解码令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenPayload(**payload)
        except JWTError as e:
            raise UnauthorizedError(message=f"Invalid token: {e}") from e

    def verify_token(self, token: str, expected_type: str = "access") -> TokenPayload:
        """验证令牌"""
        payload = self.decode_token(token)

        if payload.type != expected_type:
            raise UnauthorizedError(message=f"Invalid token type: expected {expected_type}")

        return payload
