"""Event Consumer Implementation"""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from redis.asyncio import Redis

from platform_messaging.events.base import Event

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class EventConsumer:
    """事件消费者 - 基于 Redis Streams Consumer Group"""

    def __init__(
        self,
        redis: Redis,
        group_name: str,
        consumer_name: str,
        stream_prefix: str = "events",
    ) -> None:
        self.redis = redis
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.stream_prefix = stream_prefix
        self._handlers: dict[str, list[EventHandler]] = {}
        self._running = False

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅事件类型"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")

    def on(self, event_type: str) -> Callable[[EventHandler], EventHandler]:
        """装饰器方式订阅事件"""

        def decorator(handler: EventHandler) -> EventHandler:
            self.subscribe(event_type, handler)
            return handler

        return decorator

    async def _ensure_group(self, stream_name: str) -> None:
        """确保消费者组存在"""
        try:
            await self.redis.xgroup_create(
                stream_name,
                self.group_name,
                id="0",
                mkstream=True,
            )
            logger.info(f"Created consumer group {self.group_name} for {stream_name}")
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise

    async def _process_message(
        self,
        stream_name: str,
        message_id: str,
        message: dict[str, str],
    ) -> None:
        """处理单条消息"""
        event_type = message.get("event_type", "")
        data_str = message.get("data", "{}")

        try:
            event_data = json.loads(data_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse event data: {data_str}")
            await self._ack_message(stream_name, message_id)
            return

        handlers = self._handlers.get(event_type, [])
        if not handlers:
            # 检查是否有通配符处理器
            domain = event_type.split(".")[0]
            handlers = self._handlers.get(f"{domain}.*", [])

        if not handlers:
            logger.debug(f"No handlers for event type: {event_type}")
            await self._ack_message(stream_name, message_id)
            return

        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.exception(
                    f"Handler error for {event_type}: {e}",
                    extra={
                        "event_type": event_type,
                        "message_id": message_id,
                    },
                )

        await self._ack_message(stream_name, message_id)

    async def _ack_message(self, stream_name: str, message_id: str) -> None:
        """确认消息"""
        await self.redis.xack(stream_name, self.group_name, message_id)

    async def consume(
        self,
        domains: list[str],
        batch_size: int = 10,
        block_ms: int = 5000,
    ) -> None:
        """
        开始消费事件

        Args:
            domains: 要消费的域列表 (如 ["user", "order"])
            batch_size: 每次读取的消息数量
            block_ms: 阻塞等待时间 (毫秒)
        """
        streams = {f"{self.stream_prefix}:{domain}": ">" for domain in domains}

        # 确保所有消费者组存在
        for stream_name in streams:
            await self._ensure_group(stream_name)

        self._running = True
        logger.info(
            f"Starting consumer {self.consumer_name} "
            f"in group {self.group_name} for streams: {list(streams.keys())}"
        )

        while self._running:
            try:
                results = await self.redis.xreadgroup(
                    self.group_name,
                    self.consumer_name,
                    streams,
                    count=batch_size,
                    block=block_ms,
                )

                if not results:
                    continue

                for stream_name, messages in results:
                    for message_id, message in messages:
                        await self._process_message(stream_name, message_id, message)

            except asyncio.CancelledError:
                logger.info("Consumer cancelled")
                break
            except Exception as e:
                logger.exception(f"Consumer error: {e}")
                await asyncio.sleep(1)

    def stop(self) -> None:
        """停止消费"""
        self._running = False
        logger.info(f"Stopping consumer {self.consumer_name}")

    async def claim_pending(
        self,
        domain: str,
        min_idle_time: int = 60000,
        count: int = 10,
    ) -> int:
        """
        认领超时的待处理消息

        Args:
            domain: 事件域
            min_idle_time: 最小空闲时间 (毫秒)
            count: 认领数量

        Returns:
            认领的消息数量
        """
        stream_name = f"{self.stream_prefix}:{domain}"
        claimed = 0

        try:
            # 获取待处理消息
            pending = await self.redis.xpending_range(
                stream_name,
                self.group_name,
                min="-",
                max="+",
                count=count,
            )

            for entry in pending:
                if entry.get("time_since_delivered", 0) >= min_idle_time:
                    message_id = entry.get("message_id")
                    if message_id:
                        await self.redis.xclaim(
                            stream_name,
                            self.group_name,
                            self.consumer_name,
                            min_idle_time,
                            [message_id],
                        )
                        claimed += 1

        except Exception as e:
            logger.error(f"Failed to claim pending messages: {e}")

        return claimed
