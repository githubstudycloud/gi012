"""Password Hashing Utilities"""

from passlib.context import CryptContext


class PasswordHasher:
    """密码哈希工具"""

    def __init__(self, schemes: list[str] | None = None) -> None:
        self._context = CryptContext(
            schemes=schemes or ["bcrypt"],
            deprecated="auto",
        )

    def hash(self, password: str) -> str:
        """哈希密码"""
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self._context.verify(plain_password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """检查是否需要重新哈希"""
        return self._context.needs_update(hashed_password)


# 默认实例
password_hasher = PasswordHasher()
