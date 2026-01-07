#!/usr/bin/env python3
"""生成安全密钥"""

import secrets
import base64
import hashlib


def generate_jwt_secret(length: int = 64) -> str:
    """生成 JWT 密钥"""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "pk") -> str:
    """生成 API Key"""
    random_bytes = secrets.token_bytes(32)
    key = base64.urlsafe_b64encode(random_bytes).decode().rstrip("=")
    return f"{prefix}_{key}"


def generate_password(length: int = 16) -> str:
    """生成随机密码"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_database_password() -> str:
    """生成数据库密码"""
    # 不包含特殊字符，避免 URL 编码问题
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(32))


def main():
    """主入口"""
    print("=" * 60)
    print("Platform Secret Generator")
    print("=" * 60)

    print("\n[JWT Secret Key]")
    print(f"  {generate_jwt_secret()}")

    print("\n[API Keys]")
    print(f"  Public:  {generate_api_key('pk')}")
    print(f"  Secret:  {generate_api_key('sk')}")

    print("\n[Database Password]")
    print(f"  {generate_database_password()}")

    print("\n[Random Passwords]")
    print(f"  16 chars: {generate_password(16)}")
    print(f"  32 chars: {generate_password(32)}")

    print("\n" + "=" * 60)
    print("WARNING: Store these secrets securely!")
    print("Do not commit them to version control.")
    print("=" * 60)


if __name__ == "__main__":
    main()
