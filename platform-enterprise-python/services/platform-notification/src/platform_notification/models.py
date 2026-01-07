"""Notification Models"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from platform_db import Base, TimestampMixin


class NotificationChannel(str, Enum):
    """通知渠道"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
    """通知状态"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Notification(Base, TimestampMixin):
    """通知记录模型"""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)

    # 通知信息
    channel: Mapped[str] = mapped_column(String(20), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    subject: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    template_id: Mapped[str | None] = mapped_column(String(50))

    # 接收者信息
    recipient: Mapped[str] = mapped_column(String(255))

    # 状态
    status: Mapped[str] = mapped_column(
        String(20), default=NotificationStatus.PENDING.value, index=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    # 重试
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)


class NotificationTemplate(Base, TimestampMixin):
    """通知模板模型"""

    __tablename__ = "notification_templates"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    channel: Mapped[str] = mapped_column(String(20))
    subject_template: Mapped[str | None] = mapped_column(String(255))
    content_template: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
