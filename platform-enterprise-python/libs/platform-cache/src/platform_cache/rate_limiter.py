"""Rate Limiter Implementation"""

from platform_cache.client import CacheClient


class RateLimiter:
    """速率限制器 - 基于滑动窗口算法"""

    def __init__(self, cache: CacheClient) -> None:
        self.cache = cache

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        """
        检查是否允许请求

        Args:
            key: 限流键 (如 user_id 或 ip_address)
            max_requests: 窗口内最大请求数
            window_seconds: 时间窗口 (秒)

        Returns:
            (is_allowed, remaining_requests, reset_seconds)
        """
        full_key = f"ratelimit:{key}"
        current = await self.cache.incr(full_key)

        # 首次请求，设置过期时间
        if current == 1:
            await self.cache.expire(full_key, window_seconds)

        # 获取剩余时间
        ttl = await self.cache.ttl(full_key)
        if ttl < 0:
            ttl = window_seconds

        remaining = max(0, max_requests - current)
        is_allowed = current <= max_requests

        return is_allowed, remaining, ttl

    async def reset(self, key: str) -> bool:
        """重置限流计数器"""
        return await self.cache.delete(f"ratelimit:{key}")


class TokenBucketLimiter:
    """令牌桶限流器"""

    def __init__(self, cache: CacheClient) -> None:
        self.cache = cache

    async def acquire(
        self,
        key: str,
        capacity: int,
        refill_rate: float,
        tokens: int = 1,
    ) -> tuple[bool, int]:
        """
        获取令牌

        Args:
            key: 限流键
            capacity: 桶容量
            refill_rate: 每秒补充的令牌数
            tokens: 请求的令牌数

        Returns:
            (acquired, available_tokens)
        """
        import time

        bucket_key = f"bucket:{key}"
        now = time.time()

        # 获取当前桶状态
        bucket = await self.cache.hgetall(bucket_key)

        if bucket:
            last_update = float(bucket.get("last_update", now))
            available = float(bucket.get("tokens", capacity))

            # 计算补充的令牌
            elapsed = now - last_update
            refilled = elapsed * refill_rate
            available = min(capacity, available + refilled)
        else:
            available = capacity

        # 尝试获取令牌
        if available >= tokens:
            available -= tokens
            acquired = True
        else:
            acquired = False

        # 更新桶状态
        await self.cache.hset(bucket_key, "tokens", available)
        await self.cache.hset(bucket_key, "last_update", now)
        await self.cache.expire(bucket_key, 3600)  # 1小时过期

        return acquired, int(available)
