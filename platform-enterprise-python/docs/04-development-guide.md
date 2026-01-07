# Platform Enterprise Python - 开发规范指南

## 1. 开发环境搭建

### 1.1 前置要求

| 工具 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| Python | 3.12 | 3.12.8 | 由 uv 管理 |
| uv | 0.5.0 | 最新 | 包管理器 |
| Docker | 24.0 | 最新 | 容器运行时 |
| Docker Compose | 2.20 | 最新 | 本地编排 |
| Git | 2.40 | 最新 | 版本控制 |

### 1.2 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/org/platform-enterprise-python.git
cd platform-enterprise-python

# 2. 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 安装 Python (由 uv 管理)
uv python install 3.12

# 4. 同步依赖
uv sync

# 5. 启动本地基础设施
docker compose -f deploy/docker/docker-compose.dev.yml up -d

# 6. 运行数据库迁移
uv run alembic upgrade head

# 7. 启动服务
uv run uvicorn platform_api.main:app --reload --port 8000
```

### 1.3 IDE 配置

#### VS Code 推荐扩展

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "tamasfe.even-better-toml",
        "redhat.vscode-yaml",
        "ms-azuretools.vscode-docker"
    ]
}
```

#### VS Code 设置

```json
// .vscode/settings.json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        }
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "ruff.lint.args": ["--config=ruff.toml"],
    "ruff.format.args": ["--config=ruff.toml"]
}
```

#### PyCharm 配置

1. **File Watchers** 配置 Ruff:
   - Program: `$ProjectFileDir$/.venv/bin/ruff`
   - Arguments: `format $FilePath$`

2. **External Tools** 配置类型检查:
   - Program: `$ProjectFileDir$/.venv/bin/mypy`
   - Arguments: `$FilePath$`

---

## 2. 代码规范

### 2.1 命名约定

| 类型 | 规则 | 示例 |
|------|------|------|
| 包/模块 | snake_case | `platform_core`, `user_service` |
| 类 | PascalCase | `UserService`, `AuthMiddleware` |
| 函数/方法 | snake_case | `get_user`, `create_token` |
| 变量 | snake_case | `user_id`, `access_token` |
| 常量 | UPPER_SNAKE_CASE | `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT` |
| 类型变量 | PascalCase + T 后缀 | `ModelT`, `ResponseT` |

### 2.2 文件组织

每个服务/库的标准目录结构：

```
service_name/
├── pyproject.toml           # 项目配置
├── src/
│   └── service_name/
│       ├── __init__.py      # 包入口，导出公共 API
│       ├── main.py          # 应用入口
│       ├── config.py        # 配置定义
│       ├── dependencies.py  # 依赖注入
│       ├── models/          # 数据库模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── schemas/         # Pydantic 模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/        # 业务逻辑
│       │   ├── __init__.py
│       │   └── user.py
│       ├── repositories/    # 数据访问
│       │   ├── __init__.py
│       │   └── user.py
│       └── routers/         # API 路由
│           ├── __init__.py
│           └── users.py
└── tests/
    ├── __init__.py
    ├── conftest.py          # pytest fixtures
    ├── unit/                # 单元测试
    └── integration/         # 集成测试
```

### 2.3 导入顺序

由 Ruff 自动排序，规则如下：

```python
# 1. 标准库
from datetime import datetime
from typing import Annotated, Any

# 2. 第三方库
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

# 3. 本地库 (platform-*)
from platform_core.exceptions import NotFoundError
from platform_db import BaseRepository

# 4. 当前包
from .config import settings
from .models import User
```

### 2.4 类型注解要求

**必须使用类型注解的场景**:
- 所有函数参数和返回值
- 类属性
- 全局变量

**类型注解最佳实践**:

```python
# ✅ 推荐：使用 Python 3.10+ 语法
def get_user(user_id: int) -> User | None:
    ...

# ✅ 推荐：使用 Annotated 进行依赖注入
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
) -> list[User]:
    ...

# ✅ 推荐：泛型类型
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):
    async def get(self, id: int) -> T | None:
        ...

# ❌ 避免：使用 Optional (使用 | None 代替)
def get_user(user_id: int) -> Optional[User]:  # 不推荐
    ...

# ❌ 避免：使用 Union (使用 | 代替)
def process(data: Union[str, int]) -> Union[str, int]:  # 不推荐
    ...
```

### 2.5 异步代码规范

```python
# ✅ 正确：所有 I/O 操作使用 async
async def get_user(user_id: int) -> User:
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalar_one_or_none()

# ✅ 正确：并发执行多个独立操作
async def get_dashboard_data(user_id: int) -> dict:
    user_task = asyncio.create_task(get_user(user_id))
    stats_task = asyncio.create_task(get_user_stats(user_id))
    notifications_task = asyncio.create_task(get_notifications(user_id))

    user, stats, notifications = await asyncio.gather(
        user_task, stats_task, notifications_task
    )
    return {"user": user, "stats": stats, "notifications": notifications}

# ❌ 错误：在 async 函数中执行阻塞操作
async def get_data():
    # 这会阻塞事件循环！
    response = requests.get("https://api.example.com")  # 不要这样做
    return response.json()

# ✅ 正确：使用异步 HTTP 客户端
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# ✅ 正确：如果必须使用同步代码，放到线程池
import asyncio
from functools import partial

async def cpu_bound_task(data: bytes) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(process_data, data))
```

### 2.6 异常处理规范

```python
from platform_core.exceptions import (
    NotFoundError,
    ValidationError,
    UnauthorizedError,
)

# ✅ 推荐：使用自定义业务异常
async def get_user(user_id: int) -> User:
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(
            message=f"User {user_id} not found",
            details={"user_id": user_id},
        )
    return user

# ✅ 推荐：捕获特定异常
async def create_user(data: UserCreate) -> User:
    try:
        user = await user_repo.create(data.model_dump())
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise ConflictError(message="Email already exists")
        raise

# ❌ 避免：捕获所有异常
try:
    result = await some_operation()
except Exception:  # 太宽泛
    pass

# ❌ 避免：忽略异常
try:
    result = await some_operation()
except SomeError:
    pass  # 不要这样做

# ✅ 正确：记录日志后处理
import structlog

logger = structlog.get_logger()

try:
    result = await some_operation()
except SomeError as e:
    logger.warning("operation_failed", error=str(e), operation="some_operation")
    raise  # 或者进行适当的错误处理
```

---

## 3. API 开发规范

### 3.1 路由定义

```python
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, status
from platform_core.schemas import ApiResponse, PaginatedData

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="获取用户详情",
    description="根据用户 ID 获取用户详细信息",
    responses={
        404: {"description": "用户不存在"},
    },
)
async def get_user(
    user_id: Annotated[int, Path(ge=1, description="用户 ID")],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    """
    获取用户详情

    - **user_id**: 用户的唯一标识符
    """
    user = await user_service.get_user(user_id)
    return ApiResponse(data=user)


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[UserResponse]],
    summary="列出用户",
)
async def list_users(
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
    search: Annotated[str | None, Query(max_length=100, description="搜索关键词")] = None,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[PaginatedData[UserResponse]]:
    users, total = await user_service.list_users(
        page=page,
        page_size=page_size,
        search=search,
    )
    return ApiResponse(
        data=PaginatedData.create(
            items=users,
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
)
async def create_user(
    data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    user = await user_service.create_user(data)
    return ApiResponse(data=user)


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="更新用户",
)
async def update_user(
    user_id: Annotated[int, Path(ge=1)],
    data: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    user = await user_service.update_user(user_id, data)
    return ApiResponse(data=user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
)
async def delete_user(
    user_id: Annotated[int, Path(ge=1)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    await user_service.delete_user(user_id)
```

### 3.2 Schema 定义

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """用户基础字段"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
    )

    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含至少一个数字")
        if not any(c in "!@#$%^&*()_+-=" for c in v):
            raise ValueError("密码必须包含至少一个特殊字符")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("两次密码不一致")
        return self


class UserUpdate(BaseModel):
    """更新用户请求"""
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

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
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )
```

---

## 4. 测试规范

### 4.1 测试分类

| 类型 | 目录 | 覆盖目标 | 运行时机 |
|------|------|----------|----------|
| 单元测试 | `tests/unit/` | 业务逻辑、工具函数 | 每次提交 |
| 集成测试 | `tests/integration/` | API 端点、数据库交互 | PR 合并前 |
| E2E 测试 | `tests/e2e/` | 完整业务流程 | 发布前 |
| 性能测试 | `tests/performance/` | 负载、延迟 | 定期/发布前 |

### 4.2 测试命名约定

```python
# 测试函数命名：test_<被测函数>_<场景>_<预期结果>

# 单元测试
def test_hash_password_returns_bcrypt_hash():
    ...

def test_verify_password_with_correct_password_returns_true():
    ...

def test_verify_password_with_wrong_password_returns_false():
    ...

# 异步测试
async def test_get_user_with_valid_id_returns_user():
    ...

async def test_get_user_with_invalid_id_raises_not_found():
    ...

# 参数化测试
@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("invalid", False),
    ("", False),
])
def test_validate_email(email: str, expected: bool):
    ...
```

### 4.3 Fixture 组织

```python
# conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from platform_db import Base


# ===== 基础设施 Fixtures =====

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL 测试容器"""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def redis_container():
    """Redis 测试容器"""
    with RedisContainer("redis:7-alpine") as container:
        yield container


# ===== 数据库 Fixtures =====

@pytest.fixture(scope="session")
async def db_engine(postgres_container):
    """创建数据库引擎"""
    url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话（每个测试独立事务）"""
    async with AsyncSession(db_engine) as session:
        async with session.begin():
            yield session
            await session.rollback()  # 回滚以保持测试隔离


# ===== HTTP 客户端 Fixtures =====

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端"""
    from platform_api.main import app
    from platform_api.dependencies import get_db

    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


# ===== 数据工厂 Fixtures =====

@pytest.fixture
def user_factory(db_session):
    """用户数据工厂"""
    from tests.factories import UserFactory
    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory


@pytest.fixture
async def test_user(user_factory) -> User:
    """创建测试用户"""
    return await user_factory.create(
        email="test@example.com",
        username="testuser",
        is_active=True,
    )
```

### 4.4 测试示例

```python
# tests/unit/test_auth_service.py
import pytest
from platform_auth.services.auth import AuthService


class TestAuthService:
    """认证服务测试"""

    def test_hash_password_returns_valid_hash(self):
        password = "SecurePass123!"
        hashed = AuthService.hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_verify_password_with_correct_password(self):
        password = "SecurePass123!"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_with_wrong_password(self):
        password = "SecurePass123!"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("WrongPassword", hashed) is False


# tests/integration/test_users_api.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUsersAPI:
    """用户 API 集成测试"""

    async def test_create_user_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "new@example.com"
        assert data["data"]["username"] == "newuser"
        assert "password" not in data["data"]

    async def test_create_user_duplicate_email(
        self, client: AsyncClient, test_user
    ):
        response = await client.post(
            "/api/v1/users",
            json={
                "email": test_user.email,
                "username": "another",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "CONFLICT"

    async def test_get_user_success(self, client: AsyncClient, test_user):
        response = await client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == test_user.id

    async def test_get_user_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/users/99999")

        assert response.status_code == 404

    async def test_list_users_pagination(
        self, client: AsyncClient, user_factory
    ):
        # 创建 25 个用户
        for i in range(25):
            await user_factory.create(
                email=f"user{i}@example.com",
                username=f"user{i}",
            )

        # 第一页
        response = await client.get("/api/v1/users?page=1&page_size=10")
        data = response.json()
        assert len(data["data"]["items"]) == 10
        assert data["data"]["total"] == 25
        assert data["data"]["total_pages"] == 3

        # 第三页
        response = await client.get("/api/v1/users?page=3&page_size=10")
        data = response.json()
        assert len(data["data"]["items"]) == 5
```

### 4.5 测试覆盖率

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 80
show_missing = true
```

运行测试：

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit

# 运行集成测试
uv run pytest tests/integration

# 运行特定测试文件
uv run pytest tests/unit/test_auth_service.py

# 运行带覆盖率
uv run pytest --cov --cov-report=html

# 运行标记测试
uv run pytest -m "not slow"
```

---

## 5. Git 工作流

### 5.1 分支策略

```
main (protected)
├── develop
│   ├── feature/user-management
│   ├── feature/notification-system
│   ├── bugfix/login-error
│   └── refactor/auth-module
├── release/v1.0.0
└── hotfix/security-patch
```

| 分支类型 | 命名规则 | 来源 | 合并到 |
|----------|----------|------|--------|
| main | `main` | - | - |
| develop | `develop` | main | main |
| feature | `feature/<name>` | develop | develop |
| bugfix | `bugfix/<name>` | develop | develop |
| release | `release/v<version>` | develop | main, develop |
| hotfix | `hotfix/<name>` | main | main, develop |

### 5.2 Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（不是 feat 或 fix）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具变更
- `ci`: CI/CD 变更

**示例**:

```bash
# 新功能
feat(auth): add JWT refresh token support

# Bug 修复
fix(user): correct email validation regex

# 带 body 的提交
feat(api): add rate limiting middleware

Implement token bucket algorithm for rate limiting.
- Add RateLimitMiddleware class
- Support configurable limits per endpoint
- Add Redis backend for distributed limiting

Closes #123
```

### 5.3 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff Check
        entry: uv run ruff check --fix
        language: system
        types: [python]
        pass_filenames: false

      - id: ruff-format
        name: Ruff Format
        entry: uv run ruff format
        language: system
        types: [python]
        pass_filenames: false

      - id: mypy
        name: MyPy
        entry: uv run mypy
        language: system
        types: [python]
        pass_filenames: false

      - id: pytest
        name: Pytest (fast)
        entry: uv run pytest tests/unit -x -q
        language: system
        pass_filenames: false
        stages: [push]
```

安装:

```bash
uv add --group dev pre-commit
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

---

## 6. 日志规范

### 6.1 日志级别

| 级别 | 使用场景 | 生产环境 |
|------|----------|----------|
| DEBUG | 调试信息、变量值 | 关闭 |
| INFO | 业务流程关键点 | 开启 |
| WARNING | 可恢复的问题 | 开启 |
| ERROR | 错误但不影响服务 | 开启 |
| CRITICAL | 严重错误，服务不可用 | 开启 |

### 6.2 日志内容规范

```python
import structlog

logger = structlog.get_logger()

# ✅ 推荐：结构化日志
await logger.ainfo(
    "user_login_success",
    user_id=user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
)

await logger.awarning(
    "rate_limit_exceeded",
    user_id=user.id,
    endpoint=request.url.path,
    limit=100,
    window="60s",
)

await logger.aerror(
    "database_query_failed",
    query="SELECT * FROM users",
    error=str(e),
    duration_ms=elapsed,
)

# ❌ 避免：非结构化日志
logger.info(f"User {user.id} logged in from {ip}")  # 不推荐
logger.error("Database error: " + str(e))  # 不推荐

# ❌ 避免：敏感信息
logger.info("User login", password=password)  # 绝对不要
logger.debug("Token", token=access_token)  # 绝对不要
```

### 6.3 日志配置

```python
# logging_config.py
import structlog


def configure_logging(debug: bool = False):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # 开发环境使用美化输出，生产环境使用 JSON
            structlog.dev.ConsoleRenderer() if debug
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if debug else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

---

## 7. 文档规范

### 7.1 代码文档

```python
def calculate_discount(
    original_price: float,
    discount_percent: float,
    min_price: float = 0.0,
) -> float:
    """
    计算折扣价格。

    根据原价和折扣百分比计算最终价格，确保不低于最低价格。

    Args:
        original_price: 商品原价，必须大于 0
        discount_percent: 折扣百分比，范围 0-100
        min_price: 最低价格限制，默认为 0

    Returns:
        折扣后的价格

    Raises:
        ValueError: 当 original_price <= 0 或 discount_percent 不在 0-100 范围内

    Example:
        >>> calculate_discount(100.0, 20.0)
        80.0
        >>> calculate_discount(100.0, 20.0, min_price=90.0)
        90.0
    """
    if original_price <= 0:
        raise ValueError("original_price must be positive")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")

    discounted = original_price * (1 - discount_percent / 100)
    return max(discounted, min_price)
```

### 7.2 API 文档

使用 FastAPI 自动生成 OpenAPI 文档，通过 docstring 和 Field 描述增强：

```python
@router.post(
    "/users",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="""
    创建新用户账户。

    ## 权限要求
    - 管理员：可创建任意用户
    - 普通用户：无权限

    ## 注意事项
    - 邮箱必须唯一
    - 密码至少 8 位，包含大小写字母和数字
    """,
    responses={
        201: {"description": "用户创建成功"},
        409: {"description": "邮箱已存在"},
        422: {"description": "验证失败"},
    },
)
async def create_user(
    data: UserCreate = Body(
        ...,
        example={
            "email": "user@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        },
    ),
) -> ApiResponse[UserResponse]:
    ...
```

---

## 8. 常用命令速查

```bash
# ===== 依赖管理 =====
uv sync                           # 同步所有依赖
uv add <package>                  # 添加依赖
uv add --group dev <package>      # 添加开发依赖
uv remove <package>               # 移除依赖
uv lock                           # 更新锁文件

# ===== 代码质量 =====
uv run ruff check .               # 检查代码
uv run ruff check --fix .         # 自动修复
uv run ruff format .              # 格式化代码
uv run mypy .                     # 类型检查

# ===== 测试 =====
uv run pytest                     # 运行所有测试
uv run pytest -x                  # 失败即停
uv run pytest -v                  # 详细输出
uv run pytest --cov               # 带覆盖率
uv run pytest -k "test_user"      # 运行匹配的测试

# ===== 数据库 =====
uv run alembic revision -m "msg"  # 创建迁移
uv run alembic upgrade head       # 应用迁移
uv run alembic downgrade -1       # 回滚一个版本
uv run alembic history            # 查看迁移历史

# ===== 运行服务 =====
uv run uvicorn platform_api.main:app --reload
uv run python -m platform_worker  # 启动 Worker

# ===== Docker =====
docker compose up -d              # 启动基础设施
docker compose logs -f            # 查看日志
docker compose down               # 停止服务
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-06
**作者**: Platform Architecture Team
