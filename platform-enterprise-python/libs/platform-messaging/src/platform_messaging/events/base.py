"""Base Event Classes"""

import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class EventMeta(BaseModel):
    """事件元数据"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    causation_id: str | None = None
    source: str = "platform"
    tenant_id: str | None = None
    user_id: str | None = None


class Event(BaseModel):
    """事件基类"""

    EVENT_TYPE: ClassVar[str] = "base.event"
    EVENT_VERSION: ClassVar[str] = "1.0"

    meta: EventMeta | None = None

    def model_post_init(self, __context: Any) -> None:
        """初始化后自动设置元数据"""
        if self.meta is None:
            self.meta = EventMeta(
                event_type=self.EVENT_TYPE,
                event_version=self.EVENT_VERSION,
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """从字典创建事件"""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return self.model_dump(mode="json")

    def with_correlation(self, correlation_id: str) -> "Event":
        """设置关联ID"""
        if self.meta:
            self.meta.correlation_id = correlation_id
        return self

    def with_causation(self, causation_id: str) -> "Event":
        """设置因果ID"""
        if self.meta:
            self.meta.causation_id = causation_id
        return self

    def with_tenant(self, tenant_id: str) -> "Event":
        """设置租户ID"""
        if self.meta:
            self.meta.tenant_id = tenant_id
        return self

    def with_user(self, user_id: str) -> "Event":
        """设置用户ID"""
        if self.meta:
            self.meta.user_id = user_id
        return self
