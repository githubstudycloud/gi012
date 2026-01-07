"""Notification Service Dependencies"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.exceptions import UnauthorizedError
from platform_core.security import TokenPayload

from platform_notification.config import Settings, settings
from platform_notification.service import EmailService, NotificationService


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


def get_email_service() -> EmailService:
    """获取邮件服务"""
    return EmailService()


async def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> NotificationService:
    """获取通知服务"""
    return NotificationService(session=session, email_service=email_service)


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
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
CurrentUserDep = Annotated[TokenPayload, Depends(get_current_user)]
