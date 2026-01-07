"""Auth API Routers"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from platform_core.schemas import ApiResponse
from platform_core.security import TokenPayload

from platform_auth.dependencies import AuthServiceDep, CurrentUserDep
from platform_auth.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[AuthResponse])
async def register(
    data: RegisterRequest,
    service: AuthServiceDep,
) -> ApiResponse[AuthResponse]:
    """用户注册"""
    result = await service.register(data)
    return ApiResponse(data=result, message="Registration successful")


@router.post("/login", response_model=ApiResponse[AuthResponse])
async def login(
    data: LoginRequest,
    request: Request,
    service: AuthServiceDep,
) -> ApiResponse[AuthResponse]:
    """用户登录"""
    ip_address = request.client.host if request.client else None
    result = await service.login(data, ip_address)
    return ApiResponse(data=result, message="Login successful")


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_tokens(
    data: RefreshTokenRequest,
    service: AuthServiceDep,
) -> ApiResponse[TokenResponse]:
    """刷新令牌"""
    result = await service.refresh_tokens(data.refresh_token)
    return ApiResponse(data=result, message="Token refreshed")


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    data: RefreshTokenRequest,
    service: AuthServiceDep,
) -> ApiResponse[dict]:
    """用户登出"""
    await service.logout(data.refresh_token)
    return ApiResponse(data={"success": True}, message="Logged out successfully")


@router.post("/change-password", response_model=ApiResponse[dict])
async def change_password(
    data: ChangePasswordRequest,
    request: Request,
    service: AuthServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[dict]:
    """修改密码"""
    ip_address = request.client.host if request.client else None
    await service.change_password(
        user_id=current_user.sub,
        current_password=data.current_password,
        new_password=data.new_password,
        ip_address=ip_address,
    )
    return ApiResponse(data={"success": True}, message="Password changed successfully")


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user(
    current_user: CurrentUserDep,
) -> ApiResponse[UserResponse]:
    """获取当前用户信息"""
    # 这里简化处理，实际应该从数据库获取完整用户信息
    return ApiResponse(
        data=UserResponse(
            id=current_user.sub,
            email=current_user.email or "",
            username="",
            is_active=True,
            is_superuser=False,
            email_verified=False,
            roles=current_user.roles or [],
            created_at=current_user.iat,
        ),
        message="Success",
    )
