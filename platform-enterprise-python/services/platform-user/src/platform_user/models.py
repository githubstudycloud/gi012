"""User Domain Models"""

from datetime import date

from sqlalchemy import Boolean, Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from platform_db import Base, SoftDeleteMixin, TimestampMixin


class UserProfile(Base, TimestampMixin, SoftDeleteMixin):
    """用户档案模型"""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)

    # 基本信息
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    birthday: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    location: Mapped[str | None] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))

    # 联系方式
    phone: Mapped[str | None] = mapped_column(String(20))
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 设置
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai")
    notification_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_push: Mapped[bool] = mapped_column(Boolean, default=True)


class UserAddress(Base, TimestampMixin):
    """用户地址模型"""

    __tablename__ = "user_addresses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)

    # 地址信息
    label: Mapped[str] = mapped_column(String(50), default="default")
    recipient_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(50), default="China")
    province: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    district: Mapped[str | None] = mapped_column(String(50))
    street: Mapped[str] = mapped_column(String(200))
    postal_code: Mapped[str | None] = mapped_column(String(20))

    # 状态
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
