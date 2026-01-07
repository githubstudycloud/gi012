"""User Service Layer"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from platform_core.exceptions import NotFoundError
from platform_core.utils import generate_uuid
from platform_messaging import EventPublisher, UserUpdatedEvent

from platform_user.models import UserAddress, UserProfile
from platform_user.schemas import (
    UserAddressCreate,
    UserAddressResponse,
    UserAddressUpdate,
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
)


class UserProfileService:
    """用户档案服务"""

    def __init__(
        self,
        session: AsyncSession,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self.session = session
        self.events = event_publisher

    async def get_profile(self, user_id: str) -> UserProfileResponse:
        """获取用户档案"""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise NotFoundError("User profile not found")

        return UserProfileResponse.model_validate(profile)

    async def create_profile(
        self, user_id: str, data: UserProfileCreate
    ) -> UserProfileResponse:
        """创建用户档案"""
        profile = UserProfile(
            id=generate_uuid(),
            user_id=user_id,
            **data.model_dump(),
        )
        self.session.add(profile)
        await self.session.flush()

        return UserProfileResponse.model_validate(profile)

    async def update_profile(
        self, user_id: str, data: UserProfileUpdate
    ) -> UserProfileResponse:
        """更新用户档案"""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise NotFoundError("User profile not found")

        # 记录变更
        changes = {}
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            old_value = getattr(profile, key)
            if old_value != value:
                changes[key] = (str(old_value), str(value))
                setattr(profile, key, value)

        await self.session.flush()

        # 发布事件
        if self.events and changes:
            await self.events.publish(
                UserUpdatedEvent(user_id=user_id, changes=changes)
            )

        return UserProfileResponse.model_validate(profile)

    async def get_or_create_profile(
        self, user_id: str, data: UserProfileCreate | None = None
    ) -> UserProfileResponse:
        """获取或创建用户档案"""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile:
            return UserProfileResponse.model_validate(profile)

        return await self.create_profile(user_id, data or UserProfileCreate())


class UserAddressService:
    """用户地址服务"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_addresses(self, user_id: str) -> list[UserAddressResponse]:
        """获取用户地址列表"""
        result = await self.session.execute(
            select(UserAddress)
            .where(UserAddress.user_id == user_id)
            .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        )
        addresses = result.scalars().all()
        return [UserAddressResponse.model_validate(addr) for addr in addresses]

    async def get_address(self, user_id: str, address_id: str) -> UserAddressResponse:
        """获取地址详情"""
        result = await self.session.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundError("Address not found")

        return UserAddressResponse.model_validate(address)

    async def create_address(
        self, user_id: str, data: UserAddressCreate
    ) -> UserAddressResponse:
        """创建地址"""
        # 如果设为默认，清除其他默认地址
        if data.is_default:
            await self.session.execute(
                update(UserAddress)
                .where(UserAddress.user_id == user_id)
                .values(is_default=False)
            )

        address = UserAddress(
            id=generate_uuid(),
            user_id=user_id,
            **data.model_dump(),
        )
        self.session.add(address)
        await self.session.flush()

        return UserAddressResponse.model_validate(address)

    async def update_address(
        self, user_id: str, address_id: str, data: UserAddressUpdate
    ) -> UserAddressResponse:
        """更新地址"""
        result = await self.session.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundError("Address not found")

        update_data = data.model_dump(exclude_unset=True)

        # 如果设为默认，清除其他默认地址
        if update_data.get("is_default"):
            await self.session.execute(
                update(UserAddress)
                .where(UserAddress.user_id == user_id, UserAddress.id != address_id)
                .values(is_default=False)
            )

        for key, value in update_data.items():
            setattr(address, key, value)

        await self.session.flush()
        return UserAddressResponse.model_validate(address)

    async def delete_address(self, user_id: str, address_id: str) -> bool:
        """删除地址"""
        result = await self.session.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise NotFoundError("Address not found")

        await self.session.delete(address)
        return True
