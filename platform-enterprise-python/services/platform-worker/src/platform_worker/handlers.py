"""Event Handlers"""

from typing import Any

from platform_observability import get_logger

logger = get_logger(__name__)


async def handle_user_created(event_data: dict[str, Any]) -> None:
    """处理用户创建事件"""
    user_id = event_data.get("user_id")
    email = event_data.get("email")

    logger.info(
        "Processing user.created event",
        extra={"user_id": user_id, "email": email},
    )

    # 业务逻辑：
    # 1. 发送欢迎邮件
    # 2. 初始化用户配置
    # 3. 同步到其他系统


async def handle_user_updated(event_data: dict[str, Any]) -> None:
    """处理用户更新事件"""
    user_id = event_data.get("user_id")
    changes = event_data.get("changes", {})

    logger.info(
        "Processing user.updated event",
        extra={"user_id": user_id, "changes": changes},
    )

    # 业务逻辑：
    # 1. 同步更新到搜索引擎
    # 2. 更新缓存
    # 3. 通知相关服务


async def handle_user_deleted(event_data: dict[str, Any]) -> None:
    """处理用户删除事件"""
    user_id = event_data.get("user_id")

    logger.info(
        "Processing user.deleted event",
        extra={"user_id": user_id},
    )

    # 业务逻辑：
    # 1. 清理用户数据
    # 2. 撤销所有令牌
    # 3. 发送账户删除确认邮件


async def handle_password_changed(event_data: dict[str, Any]) -> None:
    """处理密码变更事件"""
    user_id = event_data.get("user_id")
    changed_by = event_data.get("changed_by")

    logger.info(
        "Processing user.password_changed event",
        extra={"user_id": user_id, "changed_by": changed_by},
    )

    # 业务逻辑：
    # 1. 发送密码变更通知邮件
    # 2. 撤销其他会话


async def handle_notification_send(event_data: dict[str, Any]) -> None:
    """处理发送通知事件"""
    notification_type = event_data.get("type")
    recipient = event_data.get("recipient")

    logger.info(
        "Processing notification.send event",
        extra={"type": notification_type, "recipient": recipient},
    )

    # 业务逻辑：
    # 1. 根据类型选择发送渠道
    # 2. 发送通知
    # 3. 记录发送结果


# 事件处理器映射
EVENT_HANDLERS = {
    "user.created": handle_user_created,
    "user.updated": handle_user_updated,
    "user.deleted": handle_user_deleted,
    "user.password_changed": handle_password_changed,
    "notification.send": handle_notification_send,
}
