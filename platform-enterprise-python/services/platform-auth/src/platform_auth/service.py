"""Auth Service Layer"""

import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from platform_core.security import JWTHandler, PasswordHasher, TokenPayload
from platform_core.utils import generate_uuid
from platform_messaging import EventPublisher, PasswordChangedEvent, UserCreatedEvent

from platform_auth.config import settings
from platform_auth.models import RefreshToken, User, UserStatus
from platform_auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:
    """认证服务"""

    def __init__(
        self,
        session: AsyncSession,
        jwt_handler: JWTHandler,
        password_hasher: PasswordHasher,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self.session = session
        self.jwt = jwt_handler
        self.hasher = password_hasher
        self.events = event_publisher

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """用户注册"""
        # 检查邮箱是否已存在
        existing = await self.session.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Email already registered")

        # 检查用户名是否已存在
        existing = await self.session.execute(
            select(User).where(User.username == data.username)
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Username already taken")

        # 创建用户
        user = User(
            id=generate_uuid(),
            email=data.email,
            username=data.username,
            hashed_password=self.hasher.hash(data.password),
            status=UserStatus.ACTIVE.value,
            is_active=True,
            roles=json.dumps(["user"]),
        )

        self.session.add(user)
        await self.session.flush()

        # 生成令牌
        tokens = await self._create_tokens(user)

        # 发布事件
        if self.events:
            await self.events.publish(
                UserCreatedEvent(
                    user_id=user.id,
                    email=user.email,
                    username=user.username,
                    roles=json.loads(user.roles),
                )
            )

        return AuthResponse(
            user=self._to_user_response(user),
            tokens=tokens,
        )

    async def login(self, data: LoginRequest, ip_address: str | None = None) -> AuthResponse:
        """用户登录"""
        # 查找用户
        result = await self.session.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("Invalid email or password")

        # 检查账户锁定
        if user.locked_until and user.locked_until > datetime.now(UTC):
            raise UnauthorizedError("Account is temporarily locked")

        # 验证密码
        if not self.hasher.verify(data.password, user.hashed_password):
            # 增加失败次数
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
            await self.session.flush()
            raise UnauthorizedError("Invalid email or password")

        # 检查用户状态
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        # 重置失败次数，更新登录信息
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)
        user.last_login_ip = ip_address

        # 生成令牌
        tokens = await self._create_tokens(user)

        return AuthResponse(
            user=self._to_user_response(user),
            tokens=tokens,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """刷新令牌"""
        # 验证刷新令牌
        token_hash = self._hash_token(refresh_token)
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token or not stored_token.is_valid:
            raise UnauthorizedError("Invalid refresh token")

        # 获取用户
        result = await self.session.execute(
            select(User).where(User.id == stored_token.user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("User not found or disabled")

        # 撤销旧令牌
        stored_token.revoked_at = datetime.now(UTC)

        # 生成新令牌
        return await self._create_tokens(user)

    async def logout(self, refresh_token: str) -> bool:
        """登出 - 撤销刷新令牌"""
        token_hash = self._hash_token(refresh_token)
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.revoked_at = datetime.now(UTC)
            return True
        return False

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        ip_address: str | None = None,
    ) -> bool:
        """修改密码"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("User not found")

        if not self.hasher.verify(current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect")

        user.hashed_password = self.hasher.hash(new_password)

        # 发布事件
        if self.events:
            await self.events.publish(
                PasswordChangedEvent(
                    user_id=user.id,
                    changed_by="self",
                    ip_address=ip_address,
                )
            )

        return True

    async def _create_tokens(self, user: User) -> TokenResponse:
        """创建访问令牌和刷新令牌"""
        # 访问令牌
        access_token = self.jwt.encode(
            TokenPayload(
                sub=user.id,
                email=user.email,
                roles=json.loads(user.roles),
            ),
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        # 刷新令牌
        refresh_token = secrets.token_urlsafe(32)
        refresh_expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

        # 存储刷新令牌
        stored_token = RefreshToken(
            id=generate_uuid(),
            user_id=user.id,
            token_hash=self._hash_token(refresh_token),
            expires_at=refresh_expires,
        )
        self.session.add(stored_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        """哈希令牌"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _to_user_response(user: User) -> UserResponse:
        """转换为用户响应"""
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            roles=json.loads(user.roles),
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )
