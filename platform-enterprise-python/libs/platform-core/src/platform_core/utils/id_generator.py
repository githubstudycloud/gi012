"""ID Generation Utilities"""

import secrets
import uuid
from datetime import datetime


def generate_uuid() -> str:
    """生成 UUID v4"""
    return str(uuid.uuid4())


def generate_id(prefix: str = "", length: int = 16) -> str:
    """生成带前缀的随机 ID"""
    random_part = secrets.token_hex(length // 2)
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def generate_sortable_id(prefix: str = "") -> str:
    """生成可排序的 ID (基于时间戳)"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    random_part = secrets.token_hex(4)
    if prefix:
        return f"{prefix}_{timestamp}_{random_part}"
    return f"{timestamp}_{random_part}"
