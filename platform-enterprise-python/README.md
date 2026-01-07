# Platform Enterprise Python

企业级 Python 微服务平台，采用现代化工具链和最佳实践构建。

## 技术栈

- **Python 3.12+** - 最新语言特性
- **uv** - Rust 实现的超快包管理器
- **Ruff** - Rust 实现的 linter/formatter
- **FastAPI** - 现代异步 Web 框架
- **Pydantic v2** - 数据验证
- **SQLAlchemy 2.0** - 异步 ORM
- **Redis** - 缓存和消息队列
- **PostgreSQL** - 主数据库
- **Docker + Kubernetes** - 容器编排

## 项目结构

```
platform-enterprise-python/
├── docs/                    # 设计文档
├── libs/                    # 共享库
│   ├── platform-core/       # 核心工具库
│   ├── platform-db/         # 数据库抽象层
│   ├── platform-cache/      # 缓存抽象层
│   ├── platform-messaging/  # 消息队列
│   └── platform-observability/  # 可观测性
├── services/                # 微服务
│   ├── platform-api/        # API 网关
│   ├── platform-auth/       # 认证服务
│   ├── platform-user/       # 用户服务
│   ├── platform-worker/     # 后台 Worker
│   └── platform-notification/  # 通知服务
├── deploy/                  # 部署配置
│   ├── docker/              # Docker 配置
│   └── kubernetes/          # K8s 配置
├── tools/                   # 工具脚本
└── pyproject.toml           # 工作空间配置
```

## 快速开始

### 前置条件

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) 包管理器
- Docker & Docker Compose

### 安装

```bash
# 克隆仓库
git clone https://github.com/org/platform-enterprise-python.git
cd platform-enterprise-python

# 安装依赖
uv sync

# 安装 pre-commit hooks
uv run pre-commit install
```

### 启动开发环境

```bash
# 启动基础设施 (PostgreSQL, Redis, Jaeger)
make docker-up

# 或使用 docker compose
docker compose -f deploy/docker/docker-compose.yml up -d
```

### 运行服务

```bash
# 启动 API 网关
cd services/platform-api
uv run uvicorn platform_api.main:app --reload

# 启动认证服务
cd services/platform-auth
uv run uvicorn platform_auth.main:app --reload --port 8001

# 启动用户服务
cd services/platform-user
uv run uvicorn platform_user.main:app --reload --port 8002
```

## 开发

### 代码检查

```bash
# 运行 linter
make lint

# 格式化代码
make format
```

### 测试

```bash
# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov
```

### 数据库迁移

```bash
# 运行迁移
make db-migrate

# 创建新迁移
make db-revision MSG="add user table"
```

## 构建和部署

### Docker 构建

```bash
# 构建所有镜像
make build

# 构建单个服务
docker build -f deploy/docker/Dockerfile.api -t platform-api:latest .
```

### Kubernetes 部署

```bash
# 创建命名空间
kubectl apply -f deploy/kubernetes/namespace.yaml

# 部署配置
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/secrets.yaml

# 部署服务
kubectl apply -f deploy/kubernetes/api-deployment.yaml
kubectl apply -f deploy/kubernetes/auth-deployment.yaml
```

## API 文档

启动服务后访问：

- API 网关: http://localhost:8000/docs
- 认证服务: http://localhost:8001/docs
- 用户服务: http://localhost:8002/docs

## 可观测性

- **Jaeger**: http://localhost:16686 - 分布式追踪
- **Prometheus**: http://localhost:9090 - 指标收集
- **Grafana**: http://localhost:3000 - 监控面板

## 设计文档

详细设计文档位于 `docs/` 目录：

- [架构概览](docs/01-architecture-overview.md)
- [技术选型](docs/02-technology-stack.md)
- [服务设计](docs/03-service-design.md)
- [开发指南](docs/04-development-guide.md)
- [部署运维](docs/05-deployment-ops.md)

## 许可证

MIT License
