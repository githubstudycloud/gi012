"""Platform Base Exceptions"""

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
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
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


class RateLimitError(PlatformException):
    """速率限制"""

    code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests"
    status_code = 429


class ServiceUnavailableError(PlatformException):
    """服务不可用"""

    code = "SERVICE_UNAVAILABLE"
    message = "Service temporarily unavailable"
    status_code = 503
