"""Notification Service Layer"""

from datetime import UTC, datetime

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.utils import generate_uuid
from platform_observability import get_logger

from platform_notification.config import settings
from platform_notification.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationTemplate,
)
from platform_notification.schemas import (
    NotificationResponse,
    SendEmailRequest,
    SendResultResponse,
)

logger = get_logger(__name__)


class EmailService:
    """邮件服务"""

    def __init__(self) -> None:
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.use_tls = settings.smtp_use_tls
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name

    async def send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """发送邮件"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email

        # 添加纯文本版本
        if text_content:
            message.attach(MIMEText(text_content, "plain", "utf-8"))

        # 添加 HTML 版本
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            async with aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=self.use_tls,
            ) as smtp:
                if self.username and self.password:
                    await smtp.login(self.username, self.password)
                await smtp.send_message(message)

            logger.info(
                "Email sent successfully",
                extra={"to": to_email, "subject": subject},
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to send email",
                extra={"to": to_email, "error": str(e)},
            )
            raise


class NotificationService:
    """通知服务"""

    def __init__(
        self,
        session: AsyncSession,
        email_service: EmailService | None = None,
    ) -> None:
        self.session = session
        self.email_service = email_service or EmailService()

        # 模板引擎
        self.template_env = Environment(
            loader=FileSystemLoader(settings.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(self, request: SendEmailRequest) -> SendResultResponse:
        """发送邮件"""
        # 创建通知记录
        notification = Notification(
            id=generate_uuid(),
            user_id=request.user_id,
            channel=NotificationChannel.EMAIL.value,
            type="email",
            subject=request.subject,
            content=request.content,
            recipient=request.to_email,
            template_id=request.template_id,
            status=NotificationStatus.PENDING.value,
        )
        self.session.add(notification)
        await self.session.flush()

        try:
            # 渲染模板
            html_content = request.content
            if request.template_id and request.template_data:
                html_content = await self._render_template(
                    request.template_id,
                    request.template_data,
                )

            # 发送邮件
            await self.email_service.send(
                to_email=request.to_email,
                subject=request.subject,
                html_content=html_content,
            )

            # 更新状态
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.now(UTC)

            return SendResultResponse(
                notification_id=notification.id,
                status="sent",
                message="Email sent successfully",
            )

        except Exception as e:
            notification.status = NotificationStatus.FAILED.value
            notification.failed_at = datetime.now(UTC)
            notification.error_message = str(e)
            notification.retry_count += 1

            return SendResultResponse(
                notification_id=notification.id,
                status="failed",
                message=str(e),
            )

    async def get_notification(self, notification_id: str) -> NotificationResponse:
        """获取通知详情"""
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            from platform_core.exceptions import NotFoundError

            raise NotFoundError("Notification not found")

        return NotificationResponse.model_validate(notification)

    async def list_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[NotificationResponse]:
        """获取用户通知列表"""
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        notifications = result.scalars().all()
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def _render_template(
        self,
        template_id: str,
        data: dict,
    ) -> str:
        """渲染模板"""
        # 从数据库获取模板
        result = await self.session.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if template:
            jinja_template = self.template_env.from_string(template.content_template)
            return jinja_template.render(**data)

        # 尝试从文件系统加载
        try:
            jinja_template = self.template_env.get_template(f"{template_id}.html")
            return jinja_template.render(**data)
        except Exception:
            return data.get("content", "")
