# Platform Enterprise Python - 服务设计

## 1. 服务总览

### 1.1 服务矩阵

| 服务名称 | 类型 | 端口 | 职责 | 依赖 |
|----------|------|------|------|------|
| platform-api | Gateway | 8000 | API 网关、路由、限流 | auth, user |
| platform-auth | Service | 8001 | 认证、授权、令牌管理 | PostgreSQL, Redis |
| platform-user | Service | 8002 | 用户管理、租户管理 | PostgreSQL, Redis |
| platform-worker | Worker | - | 后台任务、定时任务 | Redis, RabbitMQ |
| platform-notification | Service | 8003 | 消息通知、邮件、短信 | Redis, RabbitMQ |

### 1.2 服务依赖图

```
                              ┌────────────────────┐
                              │   External Client  │
                              └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │   platform-api     │
                              │   (API Gateway)    │
                              └─────────┬──────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
    │ platform-auth   │      │ platform-user   │      │ platform-       │
    │                 │◀────▶│                 │      │ notification    │
    └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
             │                        │                        │
             │                        │                        │
             ▼                        ▼                        ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                        platform-worker                           │
    │                    (Background Tasks)                            │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 2. 共享库设计 (libs/)

### 2.1 platform-core

**职责**: 提供跨服务共享的基础设施代码

**目录结构**:
```
libs/platform-core/
├── pyproject.toml
├── src/
│   └── platform_core/
│       ├── __init__.py
│       ├── config/              # 配置管理
│       │   ├── __init__.py
│       │   └── settings.py      # BaseSettings 基类
│       ├── exceptions/          # 异常定义
│       │   ├── __init__.py
│       │   ├── base.py          # 基础异常类
│       │   └── http.py          # HTTP 异常
│       ├── schemas/             # 通用 Schema
│       │   ├── __init__.py
│       │   ├── base.py          # 基础模型
│       │   ├── pagination.py    # 分页模型
│       │   └── response.py      # 响应包装
│       ├── security/            # 安全相关
│       │   ├── __init__.py
│       │   ├── jwt.py           # JWT 处理
│       │   └── password.py      # 密码哈希
│       ├── utils/               # 工具函数
│       │   ├── __init__.py
│       │   ├── datetime.py      # 时间处理
│       │   └── id_generator.py  # ID 生成
│       └── middleware/          # 中间件
│           ├── __init__.py
│           ├── request_id.py    # 请求 ID
│           └── timing.py        # 耗时统计
└── tests/
```

**核心代码示例**:

```python
# platform_core/exceptions/base.py
from typing import Any


class PlatformException(Exception):
    """平台基础异常"""
    code: str = "PLATFORM_ERROR"
    message: str = "An unexpected error occurred"
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(PlatformException):
    """验证错误"""
    code = "VALIDATION_ERROR"
    message = "Validation failed"
    status_code = 422


class NotFoundError(PlatformException):
    """资源不存在"""
    code = "NOT_FOUND"
    message = "Resource not found"
    status_code = 404


class UnauthorizedError(PlatformException):
    """未授权"""
    code = "UNAUTHORIZED"
    message = "Authentication required"
    status_code = 401


class ForbiddenError(PlatformException):
    """禁止访问"""
    code = "FORBIDDEN"
    message = "Permission denied"
    status_code = 403


class ConflictError(PlatformException):
    """资源冲突"""
    code = "CONFLICT"
    message = "Resource conflict"
    status_code = 409
```

```python
# platform_core/schemas/response.py
from typing import Any, Generic, TypeVar
from pydantic import BaseModel


DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    """响应元数据"""
    request_id: str
    timestamp: str
    version: str = "1.0"


class ApiResponse(BaseModel, Generic[DataT]):
    """统一 API 响应格式"""
    success: bool = True
    data: DataT | None = None
    error: dict[str, Any] | None = None
    meta: ResponseMeta | None = None


class PaginatedData(BaseModel, Generic[DataT]):
    """分页数据"""
    items: list[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[DataT],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedData[DataT]":
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
```

---

### 2.2 platform-db

**职责**: 数据库抽象层、模型基类、连接管理

**目录结构**:
```
libs/platform-db/
├── pyproject.toml
├── src/
│   └── platform_db/
│       ├── __init__.py
│       ├── base.py              # 基础模型类
│       ├── mixins.py            # 模型混入
│       ├── session.py           # 会话管理
│       ├── repository.py        # 仓储基类
│       └── types.py             # 自定义类型
└── tests/
```

**核心代码示例**:

```python
# platform_db/base.py
from datetime import datetime
from typing import Any
from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 命名约定
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """所有模型的基类"""
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # 通用主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TimestampMixin:
    """时间戳混入"""
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """软删除混入"""
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True


class TenantMixin:
    """多租户混入"""
    tenant_id: Mapped[int] = mapped_column(index=True, nullable=False)
```

```python
# platform_db/repository.py
from typing import Any, Generic, Sequence, TypeVar
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """异步仓储基类"""

    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> ModelT | None:
        """根据 ID 获取"""
        return await self.session.get(self.model, id)

    async def get_by_ids(self, ids: list[int]) -> Sequence[ModelT]:
        """根据 ID 列表获取"""
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelT]:
        """获取所有记录（分页）"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """统计总数"""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, data: dict[str, Any]) -> ModelT:
        """创建记录"""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def create_many(self, data_list: list[dict[str, Any]]) -> list[ModelT]:
        """批量创建"""
        instances = [self.model(**data) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def update_by_id(self, id: int, data: dict[str, Any]) -> ModelT | None:
        """根据 ID 更新"""
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in data.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete_by_id(self, id: int) -> bool:
        """根据 ID 删除"""
        instance = await self.get_by_id(id)
        if not instance:
            return False
        await self.session.delete(instance)
        return True

    async def exists(self, id: int) -> bool:
        """检查是否存在"""
        stmt = select(func.count()).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0
```

---

### 2.3 platform-cache

**职责**: 缓存抽象层、Redis 客户端封装

```python
# platform_cache/client.py
from typing import Any
import json
from redis.asyncio import Redis


class CacheClient:
    """缓存客户端"""

    def __init__(self, redis: Redis, prefix: str = "platform"):
        self.redis = redis
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存"""
        data = await self.redis.get(self._make_key(key))
        if data:
            return json.loads(data)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int | None = None,
    ) -> bool:
        """设置缓存"""
        data = json.dumps(value, default=str)
        if expire:
            return await self.redis.setex(self._make_key(key), expire, data)
        return await self.redis.set(self._make_key(key), data)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.redis.delete(self._make_key(key)) > 0

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        keys = await self.redis.keys(self._make_key(pattern))
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def incr(self, key: str, amount: int = 1) -> int:
        """自增"""
        return await self.redis.incrby(self._make_key(key), amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.redis.expire(self._make_key(key), seconds)


class RateLimiter:
    """速率限制器"""

    def __init__(self, cache: CacheClient):
        self.cache = cache

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        检查是否允许请求

        Returns:
            (is_allowed, remaining_requests)
        """
        full_key = f"ratelimit:{key}"
        current = await self.cache.incr(full_key)

        if current == 1:
            await self.cache.expire(full_key, window_seconds)

        remaining = max(0, max_requests - current)
        return current <= max_requests, remaining
```

---

### 2.4 platform-messaging

**职责**: 消息队列抽象、事件发布订阅

```python
# platform_messaging/events.py
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
import uuid


class Event(BaseModel):
    """事件基类"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source: str
    data: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserCreatedEvent(Event):
    """用户创建事件"""
    event_type: str = "user.created"

    @classmethod
    def create(cls, user_id: int, email: str, source: str) -> "UserCreatedEvent":
        return cls(
            source=source,
            data={"user_id": user_id, "email": email},
        )


class UserUpdatedEvent(Event):
    """用户更新事件"""
    event_type: str = "user.updated"


class PasswordChangedEvent(Event):
    """密码变更事件"""
    event_type: str = "auth.password_changed"
```

```python
# platform_messaging/publisher.py
from typing import Protocol
from redis.asyncio import Redis
import json
from .events import Event


class EventPublisher(Protocol):
    """事件发布者协议"""
    async def publish(self, event: Event) -> None: ...


class RedisStreamPublisher:
    """Redis Stream 发布者"""

    def __init__(self, redis: Redis, stream_name: str = "platform:events"):
        self.redis = redis
        self.stream_name = stream_name

    async def publish(self, event: Event) -> str:
        """发布事件到 Redis Stream"""
        message_id = await self.redis.xadd(
            self.stream_name,
            {
                "event_type": event.event_type,
                "payload": event.model_dump_json(),
            },
        )
        return message_id


class RedisStreamConsumer:
    """Redis Stream 消费者"""

    def __init__(
        self,
        redis: Redis,
        stream_name: str,
        group_name: str,
        consumer_name: str,
    ):
        self.redis = redis
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name

    async def ensure_group(self) -> None:
        """确保消费者组存在"""
        try:
            await self.redis.xgroup_create(
                self.stream_name,
                self.group_name,
                id="0",
                mkstream=True,
            )
        except Exception:
            pass  # 组已存在

    async def consume(self, count: int = 10, block: int = 1000):
        """消费消息"""
        messages = await self.redis.xreadgroup(
            self.group_name,
            self.consumer_name,
            {self.stream_name: ">"},
            count=count,
            block=block,
        )
        return messages

    async def ack(self, message_id: str) -> None:
        """确认消息"""
        await self.redis.xack(self.stream_name, self.group_name, message_id)
```

---

## 3. 服务设计 (services/)

### 3.1 platform-api (API 网关)

**职责**:
- 统一入口，路由分发
- 请求验证、鉴权
- 限流、熔断
- 请求日志、链路追踪

**目录结构**:
```
services/platform-api/
├── pyproject.toml
├── src/
│   └── platform_api/
│       ├── __init__.py
│       ├── main.py              # 应用入口
│       ├── config.py            # 配置
│       ├── dependencies.py      # 依赖注入
│       ├── routers/             # 路由
│       │   ├── __init__.py
│       │   ├── health.py        # 健康检查
│       │   ├── auth.py          # 认证路由
│       │   └── users.py         # 用户路由
│       ├── middleware/          # 中间件
│       │   ├── __init__.py
│       │   ├── auth.py          # 认证中间件
│       │   └── rate_limit.py    # 限流中间件
│       └── clients/             # 服务客户端
│           ├── __init__.py
│           ├── auth.py          # 认证服务客户端
│           └── user.py          # 用户服务客户端
├── tests/
└── Dockerfile
```

**核心代码**:

```python
# platform_api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from platform_core.middleware import RequestIdMiddleware
from .config import settings
from .routers import health, auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    yield
    # 关闭


def create_app() -> FastAPI:
    app = FastAPI(
        title="Platform API Gateway",
        version="1.0.0",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url="/docs" if settings.DEBUG else None,
    )

    # 中间件
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return ORJSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": str(exc)},
            },
        )

    # 路由
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

    return app


app = create_app()
```

```python
# platform_api/middleware/rate_limit.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from platform_cache import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # 使用客户端 IP 作为限流键
        client_ip = request.client.host
        key = f"{client_ip}:{request.url.path}"

        is_allowed, remaining = await self.rate_limiter.is_allowed(
            key, self.max_requests, self.window_seconds
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"X-RateLimit-Remaining": str(remaining)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
```

---

### 3.2 platform-auth (认证授权服务)

**职责**:
- 用户认证 (登录/登出)
- JWT 令牌管理
- OAuth 2.0 / OIDC 集成
- 权限验证 (RBAC)
- 会话管理

**目录结构**:
```
services/platform-auth/
├── pyproject.toml
├── src/
│   └── platform_auth/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── models/              # 数据模型
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── role.py
│       │   └── permission.py
│       ├── schemas/             # Pydantic 模型
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── token.py
│       ├── services/            # 业务逻辑
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── token.py
│       ├── repositories/        # 数据访问
│       │   ├── __init__.py
│       │   └── user.py
│       └── routers/
│           ├── __init__.py
│           ├── auth.py
│           └── token.py
├── tests/
└── Dockerfile
```

**核心代码**:

```python
# platform_auth/services/auth.py
from datetime import datetime, timedelta
from typing import Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from platform_core.exceptions import UnauthorizedError, ValidationError
from platform_cache import CacheClient
from ..config import settings
from ..schemas.token import TokenPair, TokenPayload
from ..repositories.user import UserRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务"""

    def __init__(
        self,
        user_repo: UserRepository,
        cache: CacheClient,
    ):
        self.user_repo = user_repo
        self.cache = cache

    async def authenticate(self, email: str, password: str) -> TokenPair:
        """用户认证"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError(message="Invalid email or password")

        if not self.verify_password(password, user.hashed_password):
            raise UnauthorizedError(message="Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError(message="User account is disabled")

        # 生成令牌对
        access_token = self.create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "roles": user.role_names},
        )
        refresh_token = self.create_refresh_token(subject=str(user.id))

        # 缓存 refresh token
        await self.cache.set(
            f"refresh_token:{user.id}:{refresh_token[:16]}",
            {"user_id": user.id, "created_at": datetime.utcnow().isoformat()},
            expire=settings.JWT_REFRESH_EXPIRE_DAYS * 86400,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        """刷新令牌"""
        payload = self.decode_token(refresh_token)
        if payload.type != "refresh":
            raise UnauthorizedError(message="Invalid token type")

        # 验证 refresh token 是否在缓存中
        cache_key = f"refresh_token:{payload.sub}:{refresh_token[:16]}"
        if not await self.cache.get(cache_key):
            raise UnauthorizedError(message="Refresh token has been revoked")

        user = await self.user_repo.get_by_id(int(payload.sub))
        if not user or not user.is_active:
            raise UnauthorizedError(message="User not found or disabled")

        # 使旧的 refresh token 失效
        await self.cache.delete(cache_key)

        # 生成新的令牌对
        return await self.authenticate_by_user(user)

    async def logout(self, user_id: int, refresh_token: str) -> None:
        """登出 - 使 refresh token 失效"""
        await self.cache.delete(f"refresh_token:{user_id}:{refresh_token[:16]}")

    async def logout_all(self, user_id: int) -> None:
        """登出所有设备"""
        await self.cache.delete_pattern(f"refresh_token:{user_id}:*")

    def create_access_token(
        self,
        subject: str,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            **(additional_claims or {}),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, subject: str) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> TokenPayload:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return TokenPayload(**payload)
        except JWTError as e:
            raise UnauthorizedError(message=f"Invalid token: {e}")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
```

```python
# platform_auth/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: str
    exp: int
    iat: int
    type: str  # "access" or "refresh"
    email: str | None = None
    roles: list[str] | None = None
```

---

### 3.3 platform-user (用户服务)

**职责**:
- 用户 CRUD
- 用户资料管理
- 租户管理
- 组织架构

**目录结构**:
```
services/platform-user/
├── pyproject.toml
├── src/
│   └── platform_user/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── tenant.py
│       │   └── organization.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   └── user.py
│       └── routers/
│           ├── __init__.py
│           └── users.py
├── tests/
└── Dockerfile
```

**核心代码**:

```python
# platform_user/services/user.py
from platform_core.exceptions import NotFoundError, ConflictError
from platform_messaging import EventPublisher, UserCreatedEvent, UserUpdatedEvent
from ..repositories.user import UserRepository
from ..schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    """用户服务"""

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
    ):
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    async def create_user(self, data: UserCreate) -> UserResponse:
        """创建用户"""
        # 检查邮箱是否已存在
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError(message="Email already registered")

        # 检查用户名是否已存在
        existing = await self.user_repo.get_by_username(data.username)
        if existing:
            raise ConflictError(message="Username already taken")

        # 创建用户
        user = await self.user_repo.create(data.model_dump(exclude={"password_confirm"}))

        # 发布事件
        event = UserCreatedEvent.create(
            user_id=user.id,
            email=user.email,
            source="platform-user",
        )
        await self.event_publisher.publish(event)

        return UserResponse.model_validate(user)

    async def get_user(self, user_id: int) -> UserResponse:
        """获取用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message=f"User {user_id} not found")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        """更新用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message=f"User {user_id} not found")

        # 更新
        update_data = data.model_dump(exclude_unset=True)
        user = await self.user_repo.update_by_id(user_id, update_data)

        # 发布事件
        event = UserUpdatedEvent(
            source="platform-user",
            data={"user_id": user_id, "updated_fields": list(update_data.keys())},
        )
        await self.event_publisher.publish(event)

        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        """删除用户（软删除）"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message=f"User {user_id} not found")

        await self.user_repo.soft_delete(user_id)

    async def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[UserResponse], int]:
        """列出用户"""
        users, total = await self.user_repo.search(
            search=search,
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        return [UserResponse.model_validate(u) for u in users], total
```

---

### 3.4 platform-worker (后台任务服务)

**职责**:
- 异步任务处理
- 定时任务调度
- 事件消费处理

**技术选型**: arq (高性能异步任务队列)

**目录结构**:
```
services/platform-worker/
├── pyproject.toml
├── src/
│   └── platform_worker/
│       ├── __init__.py
│       ├── main.py              # Worker 入口
│       ├── config.py
│       ├── tasks/               # 任务定义
│       │   ├── __init__.py
│       │   ├── email.py         # 邮件任务
│       │   ├── cleanup.py       # 清理任务
│       │   └── sync.py          # 同步任务
│       ├── consumers/           # 事件消费者
│       │   ├── __init__.py
│       │   └── user.py          # 用户事件消费
│       └── cron/                # 定时任务
│           ├── __init__.py
│           └── jobs.py
├── tests/
└── Dockerfile
```

**核心代码**:

```python
# platform_worker/main.py
from arq import create_pool, cron
from arq.connections import RedisSettings
from .config import settings
from .tasks import email, cleanup, sync


async def startup(ctx):
    """Worker 启动时执行"""
    ctx["db"] = await create_db_pool()
    ctx["cache"] = await create_cache_client()


async def shutdown(ctx):
    """Worker 关闭时执行"""
    await ctx["db"].close()
    await ctx["cache"].close()


class WorkerSettings:
    """Worker 配置"""
    redis_settings = RedisSettings.from_dsn(str(settings.REDIS_URL))

    # 任务函数
    functions = [
        email.send_email,
        email.send_bulk_email,
        cleanup.cleanup_expired_sessions,
        sync.sync_user_data,
    ]

    # 定时任务
    cron_jobs = [
        cron(
            cleanup.cleanup_expired_sessions,
            hour=3,
            minute=0,
        ),  # 每天凌晨3点清理过期会话
        cron(
            sync.sync_user_data,
            minute={0, 30},
        ),  # 每30分钟同步一次
    ]

    on_startup = startup
    on_shutdown = shutdown

    # 并发配置
    max_jobs = 10
    job_timeout = 300
    keep_result = 3600
    retry_jobs = True
    max_tries = 3
```

```python
# platform_worker/tasks/email.py
from typing import Any
import structlog

logger = structlog.get_logger()


async def send_email(
    ctx: dict[str, Any],
    to: str,
    subject: str,
    body: str,
    template: str | None = None,
) -> dict[str, Any]:
    """发送单封邮件"""
    logger.info("sending_email", to=to, subject=subject)

    # 实际发送逻辑
    # await email_client.send(to, subject, body)

    return {"status": "sent", "to": to}


async def send_bulk_email(
    ctx: dict[str, Any],
    recipients: list[str],
    subject: str,
    body: str,
) -> dict[str, Any]:
    """批量发送邮件"""
    logger.info("sending_bulk_email", count=len(recipients))

    results = []
    for recipient in recipients:
        # await email_client.send(recipient, subject, body)
        results.append({"to": recipient, "status": "sent"})

    return {"total": len(recipients), "results": results}
```

```python
# platform_worker/consumers/user.py
import structlog
from platform_messaging import RedisStreamConsumer, Event

logger = structlog.get_logger()


class UserEventConsumer:
    """用户事件消费者"""

    def __init__(self, consumer: RedisStreamConsumer):
        self.consumer = consumer
        self.handlers = {
            "user.created": self.handle_user_created,
            "user.updated": self.handle_user_updated,
        }

    async def start(self):
        """启动消费者"""
        await self.consumer.ensure_group()

        while True:
            messages = await self.consumer.consume(count=10)
            for stream, entries in messages:
                for message_id, data in entries:
                    await self.process_message(message_id, data)

    async def process_message(self, message_id: str, data: dict):
        """处理消息"""
        event_type = data.get("event_type")
        handler = self.handlers.get(event_type)

        if handler:
            try:
                payload = json.loads(data.get("payload", "{}"))
                await handler(Event(**payload))
                await self.consumer.ack(message_id)
            except Exception as e:
                logger.error("event_processing_failed", error=str(e))
        else:
            logger.warning("unknown_event_type", event_type=event_type)

    async def handle_user_created(self, event: Event):
        """处理用户创建事件"""
        logger.info("user_created", user_id=event.data.get("user_id"))
        # 发送欢迎邮件、初始化用户数据等

    async def handle_user_updated(self, event: Event):
        """处理用户更新事件"""
        logger.info("user_updated", user_id=event.data.get("user_id"))
        # 同步缓存、通知相关服务等
```

---

### 3.5 platform-notification (通知服务)

**职责**:
- 站内消息
- 邮件通知
- 短信通知
- 推送通知

**目录结构**:
```
services/platform-notification/
├── pyproject.toml
├── src/
│   └── platform_notification/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── notification.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── notification.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── notification.py
│       ├── channels/            # 通知渠道
│       │   ├── __init__.py
│       │   ├── base.py          # 渠道基类
│       │   ├── email.py         # 邮件渠道
│       │   ├── sms.py           # 短信渠道
│       │   └── push.py          # 推送渠道
│       └── routers/
│           └── notifications.py
├── tests/
└── Dockerfile
```

---

## 4. 数据库设计

### 4.1 ER 图

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│     tenants      │       │      users       │       │      roles       │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK)          │       │ id (PK)          │       │ id (PK)          │
│ name             │       │ tenant_id (FK)   │───────│ name             │
│ slug             │       │ email            │       │ description      │
│ settings (JSONB) │       │ username         │       │ permissions      │
│ created_at       │       │ hashed_password  │       │ created_at       │
│ updated_at       │       │ full_name        │       └──────────────────┘
└──────────────────┘       │ is_active        │              │
         │                 │ is_superuser     │              │
         │                 │ created_at       │       ┌──────┴──────────┐
         │                 │ updated_at       │       │   user_roles    │
         │                 └──────────────────┘       ├─────────────────┤
         │                          │                 │ user_id (FK)    │
         │                          │                 │ role_id (FK)    │
         │                          └─────────────────┤ created_at      │
         │                                            └─────────────────┘
         │
         │         ┌──────────────────┐
         └────────▶│  organizations   │
                   ├──────────────────┤
                   │ id (PK)          │
                   │ tenant_id (FK)   │
                   │ parent_id (FK)   │───┐
                   │ name             │   │
                   │ type             │   │
                   │ created_at       │◀──┘ (自引用)
                   └──────────────────┘
```

### 4.2 索引策略

```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = true;

-- 复合索引
CREATE INDEX idx_users_tenant_email ON users(tenant_id, email);

-- 全文搜索索引
CREATE INDEX idx_users_fulltext ON users USING GIN(
    to_tsvector('english', coalesce(username, '') || ' ' || coalesce(full_name, ''))
);
```

---

## 5. API 设计规范

### 5.1 RESTful 端点设计

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/auth/login | 登录 |
| POST | /api/v1/auth/refresh | 刷新令牌 |
| POST | /api/v1/auth/logout | 登出 |
| GET | /api/v1/users | 列出用户 |
| POST | /api/v1/users | 创建用户 |
| GET | /api/v1/users/{id} | 获取用户 |
| PATCH | /api/v1/users/{id} | 更新用户 |
| DELETE | /api/v1/users/{id} | 删除用户 |

### 5.2 响应格式

**成功响应**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe"
    },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

**错误响应**:
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "details": {
            "email": ["Invalid email format"]
        }
    },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

### 5.3 分页响应

```json
{
    "success": true,
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-06
**作者**: Platform Architecture Team
