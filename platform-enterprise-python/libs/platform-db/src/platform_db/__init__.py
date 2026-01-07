"""Platform DB - 数据库抽象层"""

from platform_db.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin
from platform_db.repository import BaseRepository
from platform_db.session import DatabaseManager, get_db_session

__version__ = "1.0.0"

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantMixin",
    "BaseRepository",
    "DatabaseManager",
    "get_db_session",
]
