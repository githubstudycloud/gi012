"""User Service Dependencies"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.exceptions import UnauthorizedError
from platform_core.security import TokenPayload
from platform_messaging import EventPublisher

from platform_user.config import Settings, settings
from platform_user.service import UserAddressService, UserProfileService


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


async def get_event_publisher(request: Request) -> EventPublisher | None:
    """获取事件发布器"""
    redis = request.app.state.redis
    if redis:
        return EventPublisher(redis)
    return None


async def get_user_profile_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    event_publisher: Annotated[EventPublisher | None, Depends(get_event_publisher)],
) -> UserProfileService:
    """获取用户档案服务"""
    return UserProfileService(session=session, event_publisher=event_publisher)


async def get_user_address_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserAddressService:
    """获取用户地址服务"""
    return UserAddressService(session=session)


async def get_current_user(request: Request) -> TokenPayload:
    """从请求头获取当前用户"""
    user_id = request.headers.get("X-User-Id")
    user_roles = request.headers.get("X-User-Roles", "")

    if not user_id:
        raise UnauthorizedError("User not authenticated")

    return TokenPayload(
        sub=user_id,
        roles=user_roles.split(",") if user_roles else [],
    )


# 类型别名
SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]
UserProfileServiceDep = Annotated[UserProfileService, Depends(get_user_profile_service)]
UserAddressServiceDep = Annotated[UserAddressService, Depends(get_user_address_service)]
CurrentUserDep = Annotated[TokenPayload, Depends(get_current_user)]
