"""Notification API Routers"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from platform_core.schemas import ApiResponse

from platform_notification.dependencies import CurrentUserDep, NotificationServiceDep
from platform_notification.schemas import (
    NotificationResponse,
    SendEmailRequest,
    SendResultResponse,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/email", response_model=ApiResponse[SendResultResponse])
async def send_email(
    request: SendEmailRequest,
    service: NotificationServiceDep,
) -> ApiResponse[SendResultResponse]:
    """发送邮件"""
    result = await service.send_email(request)
    return ApiResponse(data=result, message="Email queued for delivery")


@router.get("/me", response_model=ApiResponse[list[NotificationResponse]])
async def list_my_notifications(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ApiResponse[list[NotificationResponse]]:
    """获取我的通知列表"""
    notifications = await service.list_user_notifications(
        user_id=current_user.sub,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(data=notifications)


@router.get("/{notification_id}", response_model=ApiResponse[NotificationResponse])
async def get_notification(
    notification_id: str,
    service: NotificationServiceDep,
) -> ApiResponse[NotificationResponse]:
    """获取通知详情"""
    notification = await service.get_notification(notification_id)
    return ApiResponse(data=notification)
