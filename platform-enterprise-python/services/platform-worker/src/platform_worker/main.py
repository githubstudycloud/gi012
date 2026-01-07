"""Platform Worker - Main Application"""

import asyncio
import signal
from typing import Any

from redis.asyncio import Redis

from platform_db import DatabaseManager
from platform_messaging import EventConsumer
from platform_observability import configure_logging, get_logger

from platform_worker.config import settings
from platform_worker.handlers import EVENT_HANDLERS

logger = get_logger(__name__)


class WorkerApp:
    """Worker 应用"""

    def __init__(self) -> None:
        self.redis: Redis | None = None
        self.db_manager: DatabaseManager | None = None
        self.consumer: EventConsumer | None = None
        self._shutdown_event = asyncio.Event()

    async def startup(self) -> None:
        """启动应用"""
        # 配置日志
        configure_logging(
            level=settings.log_level,
            json_format=settings.log_json,
            service_name=settings.service_name,
            environment=settings.environment,
        )

        logger.info("Starting worker application")

        # 初始化 Redis
        self.redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        # 初始化数据库
        self.db_manager = DatabaseManager(
            url=settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )

        # 初始化事件消费者
        self.consumer = EventConsumer(
            redis=self.redis,
            group_name=settings.consumer_group,
            consumer_name=settings.consumer_name,
        )

        # 注册事件处理器
        for event_type, handler in EVENT_HANDLERS.items():
            self.consumer.subscribe(event_type, handler)

        logger.info(
            "Worker started",
            extra={
                "group": settings.consumer_group,
                "consumer": settings.consumer_name,
                "domains": settings.domains,
            },
        )

    async def shutdown(self) -> None:
        """关闭应用"""
        logger.info("Shutting down worker application")

        if self.consumer:
            self.consumer.stop()

        if self.redis:
            await self.redis.close()

        if self.db_manager:
            await self.db_manager.close()

        logger.info("Worker shutdown complete")

    async def run(self) -> None:
        """运行 Worker"""
        await self.startup()

        # 设置信号处理
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: self._shutdown_event.set())

        try:
            # 启动消费者
            consume_task = asyncio.create_task(
                self.consumer.consume(
                    domains=settings.domains,
                    batch_size=settings.batch_size,
                    block_ms=settings.block_timeout_ms,
                )
            )

            # 等待关闭信号
            await self._shutdown_event.wait()

            # 取消消费任务
            consume_task.cancel()
            try:
                await consume_task
            except asyncio.CancelledError:
                pass

        finally:
            await self.shutdown()


async def main() -> None:
    """主入口"""
    app = WorkerApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
