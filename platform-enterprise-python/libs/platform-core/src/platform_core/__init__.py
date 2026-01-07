"""Platform Core - 核心基础库"""

from platform_core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PlatformException,
    UnauthorizedError,
    ValidationError,
)
from platform_core.schemas import ApiResponse, PaginatedData, ResponseMeta

__version__ = "1.0.0"

__all__ = [
    # Exceptions
    "PlatformException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    # Schemas
    "ApiResponse",
    "PaginatedData",
    "ResponseMeta",
]
