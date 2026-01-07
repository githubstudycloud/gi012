"""User Domain Events"""

from typing import ClassVar

from pydantic import EmailStr, Field

from platform_messaging.events.base import Event


class UserCreatedEvent(Event):
    """用户创建事件"""

    EVENT_TYPE: ClassVar[str] = "user.created"

    user_id: str
    email: EmailStr
    username: str
    roles: list[str] = Field(default_factory=list)
    is_active: bool = True


class UserUpdatedEvent(Event):
    """用户更新事件"""

    EVENT_TYPE: ClassVar[str] = "user.updated"

    user_id: str
    changes: dict[str, tuple[str | None, str | None]] = Field(
        default_factory=dict,
        description="Changed fields: {field_name: (old_value, new_value)}",
    )


class UserDeletedEvent(Event):
    """用户删除事件"""

    EVENT_TYPE: ClassVar[str] = "user.deleted"

    user_id: str
    reason: str | None = None
    soft_delete: bool = True


class PasswordChangedEvent(Event):
    """密码变更事件"""

    EVENT_TYPE: ClassVar[str] = "user.password_changed"

    user_id: str
    changed_by: str  # self / admin
    ip_address: str | None = None
    user_agent: str | None = None


class UserLoginEvent(Event):
    """用户登录事件"""

    EVENT_TYPE: ClassVar[str] = "user.login"

    user_id: str
    ip_address: str | None = None
    user_agent: str | None = None
    success: bool = True
    failure_reason: str | None = None


class UserLogoutEvent(Event):
    """用户登出事件"""

    EVENT_TYPE: ClassVar[str] = "user.logout"

    user_id: str
    session_id: str | None = None


class UserRoleChangedEvent(Event):
    """用户角色变更事件"""

    EVENT_TYPE: ClassVar[str] = "user.role_changed"

    user_id: str
    added_roles: list[str] = Field(default_factory=list)
    removed_roles: list[str] = Field(default_factory=list)
    changed_by: str
