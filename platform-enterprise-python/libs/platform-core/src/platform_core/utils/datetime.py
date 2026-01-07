"""DateTime Utilities"""

from datetime import datetime, timezone


def now_utc() -> datetime:
    """获取当前 UTC 时间"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """格式化日期时间"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)


def timestamp_ms() -> int:
    """获取毫秒时间戳"""
    return int(now_utc().timestamp() * 1000)
