#!/usr/bin/env python3
"""开发环境管理脚本"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent


def run_cmd(cmd: list[str], cwd: Path | None = None) -> int:
    """执行命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT_DIR)
    return result.returncode


def setup():
    """初始化开发环境"""
    print("Setting up development environment...")

    # 安装依赖
    run_cmd(["uv", "sync"])

    # 安装 pre-commit hooks
    run_cmd(["uv", "run", "pre-commit", "install"])

    print("Development environment setup complete!")


def lint():
    """运行代码检查"""
    print("Running linters...")

    # Ruff 检查
    code = run_cmd(["uv", "run", "ruff", "check", "."])
    if code != 0:
        return code

    # Ruff 格式检查
    code = run_cmd(["uv", "run", "ruff", "format", "--check", "."])
    if code != 0:
        return code

    # MyPy 类型检查
    code = run_cmd(["uv", "run", "mypy", "."])
    return code


def format_code():
    """格式化代码"""
    print("Formatting code...")
    run_cmd(["uv", "run", "ruff", "format", "."])
    run_cmd(["uv", "run", "ruff", "check", "--fix", "."])


def test(args: list[str] | None = None):
    """运行测试"""
    print("Running tests...")
    cmd = ["uv", "run", "pytest"]
    if args:
        cmd.extend(args)
    return run_cmd(cmd)


def test_cov():
    """运行测试并生成覆盖率报告"""
    print("Running tests with coverage...")
    return run_cmd([
        "uv", "run", "pytest",
        "--cov=libs",
        "--cov=services",
        "--cov-report=html",
        "--cov-report=term-missing",
    ])


def docker_up():
    """启动 Docker 开发环境"""
    print("Starting Docker services...")
    return run_cmd([
        "docker", "compose",
        "-f", "deploy/docker/docker-compose.yml",
        "up", "-d",
    ])


def docker_down():
    """停止 Docker 开发环境"""
    print("Stopping Docker services...")
    return run_cmd([
        "docker", "compose",
        "-f", "deploy/docker/docker-compose.yml",
        "down",
    ])


def docker_logs(service: str = ""):
    """查看 Docker 日志"""
    cmd = [
        "docker", "compose",
        "-f", "deploy/docker/docker-compose.yml",
        "logs", "-f",
    ]
    if service:
        cmd.append(service)
    return run_cmd(cmd)


def db_migrate():
    """运行数据库迁移"""
    print("Running database migrations...")
    services = ["platform-auth", "platform-user", "platform-notification"]
    for service in services:
        print(f"Migrating {service}...")
        run_cmd([
            "uv", "run", "alembic", "upgrade", "head"
        ], cwd=ROOT_DIR / "services" / service)


def db_revision(message: str):
    """创建数据库迁移"""
    services = ["platform-auth", "platform-user", "platform-notification"]
    for service in services:
        print(f"Creating revision for {service}...")
        run_cmd([
            "uv", "run", "alembic", "revision",
            "--autogenerate", "-m", message
        ], cwd=ROOT_DIR / "services" / service)


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: dev.py <command> [args]")
        print("\nCommands:")
        print("  setup       - Setup development environment")
        print("  lint        - Run linters")
        print("  format      - Format code")
        print("  test        - Run tests")
        print("  test-cov    - Run tests with coverage")
        print("  docker-up   - Start Docker services")
        print("  docker-down - Stop Docker services")
        print("  docker-logs - View Docker logs")
        print("  db-migrate  - Run database migrations")
        print("  db-revision - Create database revision")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "setup": setup,
        "lint": lint,
        "format": format_code,
        "test": lambda: test(args),
        "test-cov": test_cov,
        "docker-up": docker_up,
        "docker-down": docker_down,
        "docker-logs": lambda: docker_logs(args[0] if args else ""),
        "db-migrate": db_migrate,
        "db-revision": lambda: db_revision(args[0] if args else "migration"),
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        sys.exit(1)

    result = commands[command]()
    sys.exit(result or 0)


if __name__ == "__main__":
    main()
