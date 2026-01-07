"""Platform Cache - 缓存抽象层"""

from platform_cache.client import CacheClient, create_redis_pool
from platform_cache.rate_limiter import RateLimiter

__version__ = "1.0.0"

__all__ = [
    "CacheClient",
    "RateLimiter",
    "create_redis_pool",
]
