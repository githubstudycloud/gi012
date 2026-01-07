"""User Schemas"""

from datetime import date, datetime

from pydantic import BaseModel, Field


# 用户档案
class UserProfileBase(BaseModel):
    """用户档案基础模型"""

    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    birthday: date | None = None
    gender: str | None = None
    location: str | None = None
    website: str | None = None
    phone: str | None = None
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"
    notification_email: bool = True
    notification_push: bool = True


class UserProfileCreate(UserProfileBase):
    """创建用户档案"""

    pass


class UserProfileUpdate(UserProfileBase):
    """更新用户档案"""

    pass


class UserProfileResponse(UserProfileBase):
    """用户档案响应"""

    id: str
    user_id: str
    phone_verified: bool = False
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# 用户地址
class UserAddressBase(BaseModel):
    """用户地址基础模型"""

    label: str = "default"
    recipient_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=11, max_length=20)
    country: str = "China"
    province: str
    city: str
    district: str | None = None
    street: str
    postal_code: str | None = None
    is_default: bool = False


class UserAddressCreate(UserAddressBase):
    """创建用户地址"""

    pass


class UserAddressUpdate(UserAddressBase):
    """更新用户地址"""

    pass


class UserAddressResponse(UserAddressBase):
    """用户地址响应"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
