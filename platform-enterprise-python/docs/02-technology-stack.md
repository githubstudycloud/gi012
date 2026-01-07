# Platform Enterprise Python - 技术栈选型

## 1. 技术选型原则

### 1.1 选型标准

| 维度 | 权重 | 说明 |
|------|------|------|
| **性能** | 30% | 响应延迟、吞吐量、资源效率 |
| **生态成熟度** | 25% | 社区活跃度、文档质量、企业采用 |
| **开发效率** | 20% | 学习曲线、工具支持、调试体验 |
| **可维护性** | 15% | 代码质量工具、类型安全、测试便利 |
| **安全性** | 10% | 漏洞响应、安全特性、合规支持 |

### 1.2 技术雷达分类

```
┌─────────────────────────────────────────────────────────────────┐
│                        Technology Radar                         │
├────────────────┬────────────────┬────────────────┬─────────────┤
│     ADOPT      │     TRIAL      │     ASSESS     │    HOLD     │
│    (采用)      │    (试用)       │    (评估)      │   (暂缓)    │
├────────────────┼────────────────┼────────────────┼─────────────┤
│ uv             │ Polars         │ Mojo           │ Poetry      │
│ Ruff           │ msgspec        │ PyO3           │ Pipenv      │
│ FastAPI        │ Litestar       │ Pydantic AI    │ Flask       │
│ Pydantic v2    │ Piccolo ORM    │ Robyn          │ Celery 4.x  │
│ SQLAlchemy 2.0 │ arq            │ gRPC-Python    │ aiohttp     │
│ Redis 7+       │ NATS           │                │             │
│ PostgreSQL 16+ │                │                │             │
└────────────────┴────────────────┴────────────────┴─────────────┘
```

---

## 2. 核心技术栈详解

### 2.1 包管理与构建 - uv

**选择原因**:
- 比 pip 快 10-100 倍（Rust 实现）
- 单一二进制文件，无 Python 依赖
- 原生 Monorepo 工作空间支持
- 内置 Python 版本管理
- 兼容 pip requirements.txt

**版本要求**: `uv >= 0.5.0`

**核心命令**:

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 初始化项目
uv init platform-enterprise-python

# 添加依赖
uv add fastapi pydantic sqlalchemy

# 添加开发依赖
uv add --group dev pytest ruff mypy

# 同步依赖
uv sync

# 运行脚本
uv run python main.py

# 管理 Python 版本
uv python install 3.12
uv python pin 3.12
```

**工作空间配置** (`pyproject.toml`):

```toml
[tool.uv.workspace]
members = ["libs/*", "services/*"]

[tool.uv.sources]
# 工作空间内部依赖
platform-core = { workspace = true }
platform-db = { workspace = true }

# 开发时使用本地路径
requests = { path = "../vendor/requests", editable = true }

# Git 依赖
some-lib = { git = "https://github.com/org/repo", tag = "v1.0.0" }
```

---

### 2.2 代码质量 - Ruff

**选择原因**:
- 比 Flake8 快 10-100 倍（Rust 实现）
- 替代 Flake8、Black、isort、pydocstyle、pyupgrade 等
- 支持 700+ lint 规则
- 自动修复功能
- Monorepo 层级配置

**配置** (`ruff.toml`):

```toml
# 目标 Python 版本
target-version = "py312"

# 行长度
line-length = 120

# 排除目录
exclude = [
    ".venv",
    "__pycache__",
    ".git",
    "migrations",
]

[lint]
# 启用的规则集
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific rules
    "ASYNC",  # flake8-async
    "S",      # flake8-bandit (security)
]

# 忽略的规则
ignore = [
    "E501",   # 行长度由 formatter 处理
    "PLR0913", # 太多参数
]

# 允许自动修复
fixable = ["ALL"]

[lint.isort]
known-first-party = ["platform_core", "platform_db", "platform_api"]
force-single-line = false
lines-after-imports = 2

[lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG001"]  # 允许 assert 和未使用参数
"**/migrations/*.py" = ["ALL"]         # 迁移文件不检查

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "lf"
docstring-code-format = true
```

---

### 2.3 Web 框架 - FastAPI

**选择原因**:
- 高性能（基于 Starlette + Pydantic）
- 自动 OpenAPI 文档生成
- 原生异步支持
- 强类型依赖注入
- 成熟的企业级采用

**版本要求**: `fastapi >= 0.115.0`

**核心特性配置**:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    await init_db_pool()
    await init_redis_pool()
    await init_telemetry()

    yield  # 应用运行中

    # 关闭时执行
    await close_db_pool()
    await close_redis_pool()
    await shutdown_telemetry()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Platform API",
        version="1.0.0",
        description="Enterprise Platform API",
        lifespan=lifespan,
        # 生产环境关闭 docs
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 中间件（按顺序执行，后添加先执行）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    return app
```

**依赖注入最佳实践**:

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


# 数据库会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# 类型别名（推荐方式）
DbSession = Annotated[AsyncSession, Depends(get_db)]


# 当前用户依赖
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    user = await user_service.get_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# 在路由中使用
@router.get("/me")
async def get_me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
```

---

### 2.4 数据验证 - Pydantic v2

**选择原因**:
- Rust 核心，性能提升 5-50 倍
- 强大的验证器和序列化器
- 与 FastAPI 深度集成
- pydantic-settings 配置管理

**版本要求**: `pydantic >= 2.10.0`

**模型定义规范**:

```python
from datetime import datetime
from typing import Annotated
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserBase(BaseModel):
    """用户基础模型"""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除空白
        str_min_length=1,           # 字符串最小长度
        validate_default=True,      # 验证默认值
        extra="forbid",             # 禁止额外字段
        from_attributes=True,       # 支持 ORM 模式
    )

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")]
    full_name: str | None = None


class UserCreate(UserBase):
    """用户创建请求"""
    password: Annotated[str, Field(min_length=8, max_length=128)]
    password_confirm: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("两次密码不一致")
        return self


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    created_at: datetime

    # 排除敏感字段
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
            }
        }
    )
```

**配置管理 (pydantic-settings)**:

```python
from functools import lru_cache
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置 - 遵循 12-Factor App"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # 支持嵌套: DB__HOST
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    APP_NAME: str = "Platform API"
    APP_ENV: str = Field(default="development", pattern=r"^(development|staging|production)$")
    DEBUG: bool = False
    SECRET_KEY: str = Field(min_length=32)

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = Field(default=4, ge=1, le=32)

    # 数据库配置
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis 配置
    REDIS_URL: RedisDsn
    REDIS_MAX_CONNECTIONS: int = 50

    # JWT 配置
    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """缓存配置实例"""
    return Settings()


settings = get_settings()
```

---

### 2.5 ORM - SQLAlchemy 2.0

**选择原因**:
- 原生异步支持
- 强大的查询 API
- 成熟稳定，企业广泛采用
- 优秀的类型提示支持

**版本要求**: `sqlalchemy >= 2.0.0`

**模型定义**:

```python
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """基础模型类"""
    pass


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


class User(Base, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # 关系
    posts: Mapped[list["Post"]] = relationship(back_populates="author", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username!r})>"


class Post(Base, TimestampMixin):
    """文章模型"""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # 关系
    author: Mapped["User"] = relationship(back_populates="posts")
```

**异步数据库连接**:

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 创建异步引擎
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # 连接健康检查
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
```

**Repository 模式**:

```python
from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """基础仓储类"""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            return True
        return False
```

---

### 2.6 缓存 - Redis

**选择原因**:
- 高性能内存数据库
- 丰富的数据结构
- Streams 支持消息队列
- 原生集群支持

**版本要求**: `redis >= 7.0`

**客户端配置**:

```python
from redis.asyncio import Redis, ConnectionPool


def create_redis_pool() -> ConnectionPool:
    """创建 Redis 连接池"""
    return ConnectionPool.from_url(
        str(settings.REDIS_URL),
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


pool = create_redis_pool()


async def get_redis() -> Redis:
    """获取 Redis 连接"""
    return Redis(connection_pool=pool)


# 缓存装饰器
from functools import wraps
import json


def cache(expire: int = 300, prefix: str = "cache"):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()

            # 生成缓存键
            key_parts = [prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # 尝试获取缓存
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # 执行函数
            result = await func(*args, **kwargs)

            # 设置缓存
            await redis.setex(cache_key, expire, json.dumps(result))

            return result
        return wrapper
    return decorator
```

---

### 2.7 数据库 - PostgreSQL

**选择原因**:
- ACID 事务支持
- 丰富的数据类型（JSONB、Array、UUID）
- 强大的索引功能
- 成熟的复制和集群方案

**版本要求**: `PostgreSQL >= 16`

**关键配置**:

```ini
# postgresql.conf (生产环境示例)

# 连接
max_connections = 200
superuser_reserved_connections = 3

# 内存
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
work_mem = 64MB
maintenance_work_mem = 512MB

# WAL
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB

# 查询优化
random_page_cost = 1.1            # SSD
effective_io_concurrency = 200    # SSD
default_statistics_target = 100

# 日志
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000  # 记录超过 1s 的慢查询
```

---

## 3. 可观测性技术栈

### 3.1 OpenTelemetry

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def init_telemetry():
    """初始化遥测"""
    resource = Resource.create({
        "service.name": settings.APP_NAME,
        "service.version": "1.0.0",
        "deployment.environment": settings.APP_ENV,
    })

    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(),
        export_interval_millis=60000,
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)

    # Auto-instrumentation
    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
```

### 3.2 结构化日志

```python
import structlog


def configure_logging():
    """配置结构化日志"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # 生产环境使用 JSON
            structlog.processors.JSONRenderer() if settings.is_production
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO if settings.is_production else logging.DEBUG
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# 使用
logger = structlog.get_logger()

await logger.ainfo(
    "user_login",
    user_id=user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
)
```

---

## 4. 测试技术栈

### 4.1 测试框架

| 工具 | 用途 | 版本 |
|------|------|------|
| pytest | 测试框架 | >= 8.0 |
| pytest-asyncio | 异步测试支持 | >= 0.23 |
| pytest-cov | 覆盖率报告 | >= 5.0 |
| httpx | HTTP 测试客户端 | >= 0.27 |
| factory-boy | 测试数据工厂 | >= 3.3 |
| faker | 假数据生成 | >= 28.0 |
| testcontainers | 容器化测试 | >= 4.0 |

### 4.2 测试配置

```python
# conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container():
    """启动 PostgreSQL 测试容器"""
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """启动 Redis 测试容器"""
    with RedisContainer("redis:7") as redis:
        yield redis


@pytest.fixture
async def db_session(postgres_container) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    engine = create_async_engine(postgres_container.get_connection_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

---

## 5. 版本锁定

### 5.1 核心依赖版本

```toml
# pyproject.toml
[project]
dependencies = [
    # Web Framework
    "fastapi>=0.115.0,<1.0.0",
    "uvicorn[standard]>=0.32.0",
    "gunicorn>=23.0.0",

    # Data Validation
    "pydantic>=2.10.0,<3.0.0",
    "pydantic-settings>=2.6.0",

    # Database
    "sqlalchemy[asyncio]>=2.0.0,<3.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",

    # Cache
    "redis>=5.2.0",

    # Security
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",

    # Observability
    "opentelemetry-api>=1.28.0",
    "opentelemetry-sdk>=1.28.0",
    "opentelemetry-instrumentation-fastapi>=0.49b0",
    "structlog>=24.4.0",

    # Utils
    "httpx>=0.27.0",
    "tenacity>=9.0.0",
    "orjson>=3.10.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "testcontainers>=4.8.0",
    "factory-boy>=3.3.0",
    "faker>=33.0.0",
]
```

### 5.2 Python 版本

```
# .python-version
3.12.8
```

**Python 3.12 关键特性**:
- 更快的解释器（性能提升 5%）
- 改进的错误消息
- `type` 语法糖
- Per-interpreter GIL (PEP 684)

---

## 6. 技术对比与决策记录

### 6.1 为什么选择 uv 而非 Poetry？

| 维度 | uv | Poetry |
|------|-----|--------|
| 依赖解析速度 | ~1s | ~30s |
| 安装速度 | 10-100x 快 | 基准 |
| Monorepo 支持 | 原生 workspace | 插件方式 |
| Python 版本管理 | 内置 | 需要 pyenv |
| 二进制大小 | ~20MB 单文件 | 需要 Python 环境 |
| 活跃维护 | Astral (Ruff 团队) | 社区 |

**决策**: 采用 uv，获得显著的性能提升和更好的 Monorepo 支持。

### 6.2 为什么选择 FastAPI 而非 Django？

| 维度 | FastAPI | Django |
|------|---------|--------|
| 性能 | 高 (异步原生) | 中等 |
| 学习曲线 | 平缓 | 陡峭 |
| 类型支持 | 原生强类型 | 可选 |
| 微服务适配 | 非常适合 | 偏重单体 |
| Admin 面板 | 无内置 | 强大 |
| ORM | 灵活选择 | Django ORM |

**决策**: 微服务架构优先选择 FastAPI，需要快速开发管理后台时考虑 Django。

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-06
**作者**: Platform Architecture Team
