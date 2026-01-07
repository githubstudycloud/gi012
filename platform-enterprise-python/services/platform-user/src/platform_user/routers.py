"""User API Routers"""

from typing import Annotated

from fastapi import APIRouter, Depends

from platform_core.schemas import ApiResponse

from platform_user.dependencies import (
    CurrentUserDep,
    UserAddressServiceDep,
    UserProfileServiceDep,
)
from platform_user.schemas import (
    UserAddressCreate,
    UserAddressResponse,
    UserAddressUpdate,
    UserProfileResponse,
    UserProfileUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


# 用户档案路由
@router.get("/me/profile", response_model=ApiResponse[UserProfileResponse])
async def get_my_profile(
    service: UserProfileServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserProfileResponse]:
    """获取当前用户档案"""
    profile = await service.get_or_create_profile(current_user.sub)
    return ApiResponse(data=profile)


@router.put("/me/profile", response_model=ApiResponse[UserProfileResponse])
async def update_my_profile(
    data: UserProfileUpdate,
    service: UserProfileServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserProfileResponse]:
    """更新当前用户档案"""
    profile = await service.update_profile(current_user.sub, data)
    return ApiResponse(data=profile, message="Profile updated")


@router.get("/{user_id}/profile", response_model=ApiResponse[UserProfileResponse])
async def get_user_profile(
    user_id: str,
    service: UserProfileServiceDep,
) -> ApiResponse[UserProfileResponse]:
    """获取用户档案 (公开信息)"""
    profile = await service.get_profile(user_id)
    return ApiResponse(data=profile)


# 用户地址路由
@router.get("/me/addresses", response_model=ApiResponse[list[UserAddressResponse]])
async def list_my_addresses(
    service: UserAddressServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[list[UserAddressResponse]]:
    """获取我的地址列表"""
    addresses = await service.list_addresses(current_user.sub)
    return ApiResponse(data=addresses)


@router.post("/me/addresses", response_model=ApiResponse[UserAddressResponse])
async def create_address(
    data: UserAddressCreate,
    service: UserAddressServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserAddressResponse]:
    """创建地址"""
    address = await service.create_address(current_user.sub, data)
    return ApiResponse(data=address, message="Address created")


@router.get(
    "/me/addresses/{address_id}", response_model=ApiResponse[UserAddressResponse]
)
async def get_address(
    address_id: str,
    service: UserAddressServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserAddressResponse]:
    """获取地址详情"""
    address = await service.get_address(current_user.sub, address_id)
    return ApiResponse(data=address)


@router.put(
    "/me/addresses/{address_id}", response_model=ApiResponse[UserAddressResponse]
)
async def update_address(
    address_id: str,
    data: UserAddressUpdate,
    service: UserAddressServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserAddressResponse]:
    """更新地址"""
    address = await service.update_address(current_user.sub, address_id, data)
    return ApiResponse(data=address, message="Address updated")


@router.delete("/me/addresses/{address_id}", response_model=ApiResponse[dict])
async def delete_address(
    address_id: str,
    service: UserAddressServiceDep,
    current_user: CurrentUserDep,
) -> ApiResponse[dict]:
    """删除地址"""
    await service.delete_address(current_user.sub, address_id)
    return ApiResponse(data={"deleted": True}, message="Address deleted")
