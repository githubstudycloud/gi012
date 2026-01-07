#!/usr/bin/env python3
"""构建脚本"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
SERVICES = [
    "platform-api",
    "platform-auth",
    "platform-user",
    "platform-worker",
    "platform-notification",
]


def run_cmd(cmd: list[str], cwd: Path | None = None) -> int:
    """执行命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT_DIR)
    return result.returncode


def build_base(tag: str = "latest", registry: str = ""):
    """构建基础镜像"""
    print("Building base image...")
    image_name = f"{registry}platform-base:{tag}" if registry else f"platform-base:{tag}"

    return run_cmd([
        "docker", "build",
        "-f", "deploy/docker/Dockerfile.base",
        "-t", image_name,
        ".",
    ])


def build_service(service: str, tag: str = "latest", registry: str = ""):
    """构建服务镜像"""
    print(f"Building {service}...")

    dockerfile = f"deploy/docker/Dockerfile.{service.replace('platform-', '')}"
    image_name = f"{registry}{service}:{tag}" if registry else f"{service}:{tag}"

    return run_cmd([
        "docker", "build",
        "-f", dockerfile,
        "-t", image_name,
        ".",
    ])


def build_all(tag: str = "latest", registry: str = ""):
    """构建所有镜像"""
    # 先构建基础镜像
    code = build_base(tag, registry)
    if code != 0:
        return code

    # 构建所有服务
    for service in SERVICES:
        code = build_service(service, tag, registry)
        if code != 0:
            return code

    print("\nAll images built successfully!")
    return 0


def push_all(tag: str = "latest", registry: str = ""):
    """推送所有镜像"""
    if not registry:
        print("Error: Registry is required for push")
        return 1

    images = ["platform-base"] + SERVICES

    for image in images:
        image_name = f"{registry}{image}:{tag}"
        print(f"Pushing {image_name}...")
        code = run_cmd(["docker", "push", image_name])
        if code != 0:
            return code

    print("\nAll images pushed successfully!")
    return 0


def clean():
    """清理构建产物"""
    print("Cleaning build artifacts...")

    # 清理 Python 缓存
    for pattern in ["**/__pycache__", "**/*.pyc", "**/.pytest_cache", "**/.mypy_cache"]:
        for path in ROOT_DIR.glob(pattern):
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                path.unlink()

    # 清理 Docker 构建缓存
    run_cmd(["docker", "system", "prune", "-f"])

    print("Clean complete!")
    return 0


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Build script for platform services")
    parser.add_argument("command", choices=["build", "build-all", "push", "clean"])
    parser.add_argument("--service", "-s", help="Service to build")
    parser.add_argument("--tag", "-t", default="latest", help="Image tag")
    parser.add_argument("--registry", "-r", default="", help="Container registry")

    args = parser.parse_args()

    if args.command == "build":
        if args.service:
            sys.exit(build_service(args.service, args.tag, args.registry))
        else:
            sys.exit(build_base(args.tag, args.registry))

    elif args.command == "build-all":
        sys.exit(build_all(args.tag, args.registry))

    elif args.command == "push":
        sys.exit(push_all(args.tag, args.registry))

    elif args.command == "clean":
        sys.exit(clean())


if __name__ == "__main__":
    main()
