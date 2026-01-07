"""Redis Cache Client"""

import json
from typing import Any

from redis.asyncio import ConnectionPool, Redis


def create_redis_pool(
    url: str,
    max_connections: int = 50,
    decode_responses: bool = True,
) -> ConnectionPool:
    """创建 Redis 连接池"""
    return ConnectionPool.from_url(
        url,
        max_connections=max_connections,
        decode_responses=decode_responses,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


class CacheClient:
    """缓存客户端"""

    def __init__(
        self,
        redis: Redis,
        prefix: str = "platform",
        default_ttl: int = 300,
    ) -> None:
        self.redis = redis
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存"""
        data = await self.redis.get(self._make_key(key))
        if data:
            return json.loads(data)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """设置缓存"""
        data = json.dumps(value, default=str)
        expire = ttl or self.default_ttl
        result = await self.redis.setex(self._make_key(key), expire, data)
        return bool(result)

    async def set_nx(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """设置缓存 (仅当键不存在时)"""
        data = json.dumps(value, default=str)
        expire = ttl or self.default_ttl
        result = await self.redis.set(
            self._make_key(key),
            data,
            ex=expire,
            nx=True,
        )
        return bool(result)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        result = await self.redis.delete(self._make_key(key))
        return result > 0

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        full_pattern = self._make_key(pattern)
        keys = []
        async for key in self.redis.scan_iter(full_pattern):
            keys.append(key)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.redis.exists(self._make_key(key)) > 0

    async def incr(self, key: str, amount: int = 1) -> int:
        """自增"""
        return await self.redis.incrby(self._make_key(key), amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """自减"""
        return await self.redis.decrby(self._make_key(key), amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.redis.expire(self._make_key(key), seconds)

    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return await self.redis.ttl(self._make_key(key))

    async def hget(self, name: str, key: str) -> Any | None:
        """获取哈希字段"""
        data = await self.redis.hget(self._make_key(name), key)
        if data:
            return json.loads(data)
        return None

    async def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希字段"""
        data = json.dumps(value, default=str)
        return await self.redis.hset(self._make_key(name), key, data)

    async def hgetall(self, name: str) -> dict[str, Any]:
        """获取所有哈希字段"""
        data = await self.redis.hgetall(self._make_key(name))
        return {k: json.loads(v) for k, v in data.items()}

    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        return await self.redis.hdel(self._make_key(name), *keys)
