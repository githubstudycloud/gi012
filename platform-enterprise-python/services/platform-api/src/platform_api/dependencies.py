"""Dependency Injection"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient
from redis.asyncio import Redis

from platform_cache import CacheClient, RateLimiter
from platform_core.security import JWTHandler, TokenPayload

from platform_api.config import Settings, settings


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return settings


async def get_redis(request: Request) -> Redis:
    """获取 Redis 连接"""
    return request.app.state.redis


async def get_cache(
    redis: Annotated[Redis, Depends(get_redis)],
) -> CacheClient:
    """获取缓存客户端"""
    return CacheClient(redis, prefix="api")


async def get_rate_limiter(
    cache: Annotated[CacheClient, Depends(get_cache)],
) -> RateLimiter:
    """获取限流器"""
    return RateLimiter(cache)


async def get_jwt_handler(
    config: Annotated[Settings, Depends(get_settings)],
) -> JWTHandler:
    """获取 JWT 处理器"""
    return JWTHandler(
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )


async def get_http_client(request: Request) -> AsyncClient:
    """获取 HTTP 客户端"""
    return request.app.state.http_client


async def get_current_user(
    request: Request,
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
) -> TokenPayload:
    """获取当前用户"""
    from platform_core.exceptions import UnauthorizedError

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing authorization token")

    token = auth_header.split(" ")[1]
    payload = jwt_handler.decode(token)

    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    return payload


async def get_optional_user(
    request: Request,
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
) -> TokenPayload | None:
    """获取可选的当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    return jwt_handler.decode(token)


# 类型别名
SettingsDep = Annotated[Settings, Depends(get_settings)]
RedisDep = Annotated[Redis, Depends(get_redis)]
CacheDep = Annotated[CacheClient, Depends(get_cache)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]
JWTHandlerDep = Annotated[JWTHandler, Depends(get_jwt_handler)]
HttpClientDep = Annotated[AsyncClient, Depends(get_http_client)]
CurrentUserDep = Annotated[TokenPayload, Depends(get_current_user)]
OptionalUserDep = Annotated[TokenPayload | None, Depends(get_optional_user)]
