"""Platform Messaging - 事件驱动消息系统"""

from platform_messaging.events.base import Event, EventMeta
from platform_messaging.events.user import (
    PasswordChangedEvent,
    UserCreatedEvent,
    UserDeletedEvent,
    UserUpdatedEvent,
)
from platform_messaging.publisher import EventPublisher
from platform_messaging.consumer import EventConsumer

__version__ = "1.0.0"

__all__ = [
    "Event",
    "EventMeta",
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserDeletedEvent",
    "PasswordChangedEvent",
    "EventPublisher",
    "EventConsumer",
]
