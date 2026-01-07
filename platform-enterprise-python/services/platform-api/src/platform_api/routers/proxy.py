"""Proxy Router - Routes requests to backend services"""

from typing import Any

from fastapi import APIRouter, Request, Response

from platform_core.schemas import ApiResponse

from platform_api.dependencies import (
    CurrentUserDep,
    HttpClientDep,
    OptionalUserDep,
    SettingsDep,
)

router = APIRouter()


async def proxy_request(
    client: HttpClientDep,
    base_url: str,
    path: str,
    request: Request,
    user: Any | None = None,
) -> Response:
    """代理请求到后端服务"""
    # 构建目标 URL
    url = f"{base_url}/{path}"

    # 复制请求头
    headers = dict(request.headers)
    headers.pop("host", None)

    # 添加用户信息
    if user:
        headers["X-User-Id"] = user.sub
        headers["X-User-Roles"] = ",".join(user.roles or [])

    # 获取请求体
    body = await request.body()

    # 发送请求
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
        params=request.query_params,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


# Auth Service 路由
@router.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def auth_proxy(
    path: str,
    request: Request,
    client: HttpClientDep,
    settings: SettingsDep,
    user: OptionalUserDep,
) -> Response:
    """代理认证服务请求"""
    return await proxy_request(
        client,
        settings.auth_service_url,
        path,
        request,
        user,
    )


# User Service 路由
@router.api_route(
    "/users/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def users_proxy(
    path: str,
    request: Request,
    client: HttpClientDep,
    settings: SettingsDep,
    user: CurrentUserDep,
) -> Response:
    """代理用户服务请求 (需要认证)"""
    return await proxy_request(
        client,
        settings.user_service_url,
        f"users/{path}",
        request,
        user,
    )


# 公开端点
@router.get("/public/health")
async def public_health() -> ApiResponse[dict]:
    """公开健康检查"""
    return ApiResponse(data={"status": "ok"}, message="Service is healthy")
