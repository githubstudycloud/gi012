"""Event Publisher Implementation"""

import json
import logging
from typing import Any

from redis.asyncio import Redis

from platform_messaging.events.base import Event

logger = logging.getLogger(__name__)


class EventPublisher:
    """事件发布器 - 基于 Redis Streams"""

    def __init__(
        self,
        redis: Redis,
        stream_prefix: str = "events",
        max_len: int = 10000,
    ) -> None:
        self.redis = redis
        self.stream_prefix = stream_prefix
        self.max_len = max_len

    def _get_stream_name(self, event: Event) -> str:
        """获取事件对应的 Stream 名称"""
        event_type = event.EVENT_TYPE
        # user.created -> events:user
        domain = event_type.split(".")[0]
        return f"{self.stream_prefix}:{domain}"

    async def publish(self, event: Event) -> str:
        """
        发布事件到 Redis Stream

        Args:
            event: 要发布的事件

        Returns:
            消息ID
        """
        stream_name = self._get_stream_name(event)
        event_data = event.to_dict()

        # Redis Stream 要求 field 是字符串
        message = {
            "event_type": event.EVENT_TYPE,
            "event_id": event.meta.event_id if event.meta else "",
            "data": json.dumps(event_data, default=str),
        }

        message_id = await self.redis.xadd(
            stream_name,
            message,
            maxlen=self.max_len,
            approximate=True,
        )

        logger.info(
            "Event published",
            extra={
                "stream": stream_name,
                "message_id": message_id,
                "event_type": event.EVENT_TYPE,
                "event_id": event.meta.event_id if event.meta else None,
            },
        )

        return message_id

    async def publish_batch(self, events: list[Event]) -> list[str]:
        """批量发布事件"""
        message_ids = []
        for event in events:
            msg_id = await self.publish(event)
            message_ids.append(msg_id)
        return message_ids

    async def get_stream_info(self, domain: str) -> dict[str, Any]:
        """获取 Stream 信息"""
        stream_name = f"{self.stream_prefix}:{domain}"
        try:
            info = await self.redis.xinfo_stream(stream_name)
            return {
                "length": info.get("length", 0),
                "first_entry": info.get("first-entry"),
                "last_entry": info.get("last-entry"),
                "groups": info.get("groups", 0),
            }
        except Exception:
            return {"length": 0, "error": "Stream not found"}
