.PHONY: help setup lint format test test-cov docker-up docker-down build clean

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
help:
	@echo "Platform Enterprise Python - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  setup       - Setup development environment"
	@echo "  lint        - Run linters (ruff + mypy)"
	@echo "  format      - Format code with ruff"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up   - Start all services with docker-compose"
	@echo "  docker-down - Stop all services"
	@echo "  docker-logs - View service logs"
	@echo ""
	@echo "Build:"
	@echo "  build       - Build all Docker images"
	@echo "  build-base  - Build base image only"
	@echo "  push        - Push images to registry"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-revision - Create new migration"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       - Clean build artifacts"

# 开发环境设置
setup:
	uv sync
	uv run pre-commit install
	@echo "Development environment setup complete!"

# 代码检查
lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .

# 代码格式化
format:
	uv run ruff format .
	uv run ruff check --fix .

# 测试
test:
	uv run pytest

test-cov:
	uv run pytest --cov=libs --cov=services --cov-report=html --cov-report=term-missing

# Docker 操作
docker-up:
	docker compose -f deploy/docker/docker-compose.yml up -d

docker-down:
	docker compose -f deploy/docker/docker-compose.yml down

docker-logs:
	docker compose -f deploy/docker/docker-compose.yml logs -f

# 构建
build-base:
	docker build -f deploy/docker/Dockerfile.base -t platform-base:latest .

build: build-base
	docker build -f deploy/docker/Dockerfile.api -t platform-api:latest .
	docker build -f deploy/docker/Dockerfile.auth -t platform-auth:latest .
	docker build -f deploy/docker/Dockerfile.user -t platform-user:latest .
	docker build -f deploy/docker/Dockerfile.worker -t platform-worker:latest .
	docker build -f deploy/docker/Dockerfile.notification -t platform-notification:latest .

push:
	@echo "Usage: make push REGISTRY=your-registry.com/"
	@test -n "$(REGISTRY)" || (echo "REGISTRY is required" && exit 1)
	docker push $(REGISTRY)platform-base:latest
	docker push $(REGISTRY)platform-api:latest
	docker push $(REGISTRY)platform-auth:latest
	docker push $(REGISTRY)platform-user:latest
	docker push $(REGISTRY)platform-worker:latest
	docker push $(REGISTRY)platform-notification:latest

# 数据库迁移
db-migrate:
	cd services/platform-auth && uv run alembic upgrade head
	cd services/platform-user && uv run alembic upgrade head
	cd services/platform-notification && uv run alembic upgrade head

db-revision:
	@test -n "$(MSG)" || (echo "MSG is required. Usage: make db-revision MSG='your message'" && exit 1)
	cd services/platform-auth && uv run alembic revision --autogenerate -m "$(MSG)"
	cd services/platform-user && uv run alembic revision --autogenerate -m "$(MSG)"
	cd services/platform-notification && uv run alembic revision --autogenerate -m "$(MSG)"

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
