"""Auth Service Dependencies"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.exceptions import UnauthorizedError
from platform_core.security import JWTHandler, PasswordHasher, TokenPayload
from platform_messaging import EventPublisher

from platform_auth.config import Settings, settings
from platform_auth.service import AuthService


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return settings


async def get_db_session(request: Request) -> AsyncSession:
    """获取数据库会话"""
    async with request.app.state.db_manager.session() as session:
        yield session


async def get_redis(request: Request) -> Redis:
    """获取 Redis 连接"""
    return request.app.state.redis


def get_jwt_handler(
    config: Annotated[Settings, Depends(get_settings)],
) -> JWTHandler:
    """获取 JWT 处理器"""
    return JWTHandler(
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )


def get_password_hasher() -> PasswordHasher:
    """获取密码哈希器"""
    return PasswordHasher()


async def get_event_publisher(request: Request) -> EventPublisher | None:
    """获取事件发布器"""
    redis = request.app.state.redis
    if redis:
        return EventPublisher(redis)
    return None


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    event_publisher: Annotated[EventPublisher | None, Depends(get_event_publisher)],
) -> AuthService:
    """获取认证服务"""
    return AuthService(
        session=session,
        jwt_handler=jwt_handler,
        password_hasher=password_hasher,
        event_publisher=event_publisher,
    )


async def get_current_user(
    request: Request,
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
) -> TokenPayload:
    """获取当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing authorization token")

    token = auth_header.split(" ")[1]
    payload = jwt_handler.decode(token)

    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    return payload


# 类型别名
SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]
JWTHandlerDep = Annotated[JWTHandler, Depends(get_jwt_handler)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[TokenPayload, Depends(get_current_user)]
