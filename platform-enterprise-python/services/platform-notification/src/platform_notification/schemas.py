"""Notification Schemas"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class NotificationChannel(str, Enum):
    """通知渠道"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """通知状态"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


# 请求模型
class SendEmailRequest(BaseModel):
    """发送邮件请求"""

    user_id: str
    to_email: EmailStr
    subject: str
    content: str
    template_id: str | None = None
    template_data: dict | None = None


class SendSmsRequest(BaseModel):
    """发送短信请求"""

    user_id: str
    phone: str = Field(min_length=11)
    content: str = Field(max_length=500)
    template_id: str | None = None
    template_data: dict | None = None


class SendPushRequest(BaseModel):
    """发送推送请求"""

    user_id: str
    title: str
    body: str
    data: dict | None = None


class SendBatchRequest(BaseModel):
    """批量发送请求"""

    user_ids: list[str]
    channel: NotificationChannel
    subject: str | None = None
    content: str
    template_id: str | None = None
    template_data: dict | None = None


# 响应模型
class NotificationResponse(BaseModel):
    """通知响应"""

    id: str
    user_id: str
    channel: str
    type: str
    subject: str | None
    recipient: str
    status: str
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SendResultResponse(BaseModel):
    """发送结果响应"""

    notification_id: str
    status: str
    message: str | None = None
