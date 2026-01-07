"""Health Check Utilities"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class ComponentHealth:
    """组件健康状态"""

    name: str
    status: HealthStatus
    message: str | None = None
    latency_ms: float | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    """健康检查报告"""

    status: HealthStatus
    timestamp: datetime
    version: str
    components: list[ComponentHealth]
    uptime_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                    "details": c.details,
                }
                for c in self.components
            ],
        }


HealthChecker = Callable[[], Awaitable[ComponentHealth]]


class HealthCheck:
    """健康检查管理器"""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
    ) -> None:
        self.service_name = service_name
        self.version = version
        self._checkers: dict[str, HealthChecker] = {}
        self._start_time = datetime.now(UTC)

    def register(
        self,
        name: str,
        checker: HealthChecker,
    ) -> None:
        """注册健康检查器"""
        self._checkers[name] = checker

    def checker(self, name: str) -> Callable[[HealthChecker], HealthChecker]:
        """装饰器方式注册检查器"""

        def decorator(func: HealthChecker) -> HealthChecker:
            self.register(name, func)
            return func

        return decorator

    async def check(self, timeout: float = 5.0) -> HealthReport:
        """执行所有健康检查"""
        components: list[ComponentHealth] = []
        overall_status = HealthStatus.HEALTHY

        for name, checker in self._checkers.items():
            try:
                start = asyncio.get_event_loop().time()
                result = await asyncio.wait_for(checker(), timeout=timeout)
                result.latency_ms = (asyncio.get_event_loop().time() - start) * 1000
                components.append(result)

                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif (
                    result.status == HealthStatus.DEGRADED
                    and overall_status != HealthStatus.UNHEALTHY
                ):
                    overall_status = HealthStatus.DEGRADED

            except asyncio.TimeoutError:
                components.append(
                    ComponentHealth(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check timed out after {timeout}s",
                    )
                )
                overall_status = HealthStatus.UNHEALTHY

            except Exception as e:
                components.append(
                    ComponentHealth(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=str(e),
                    )
                )
                overall_status = HealthStatus.UNHEALTHY

        uptime = (datetime.now(UTC) - self._start_time).total_seconds()

        return HealthReport(
            status=overall_status,
            timestamp=datetime.now(UTC),
            version=self.version,
            components=components,
            uptime_seconds=uptime,
        )

    async def liveness(self) -> dict[str, Any]:
        """存活检查 (快速)"""
        return {
            "status": "ok",
            "service": self.service_name,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def readiness(self) -> HealthReport:
        """就绪检查 (完整)"""
        return await self.check()


# 预定义的检查器工厂
async def create_redis_checker(redis: Any) -> ComponentHealth:
    """Redis 健康检查"""
    try:
        await redis.ping()
        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Connected",
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def create_database_checker(session_factory: Any) -> ComponentHealth:
    """数据库健康检查"""
    try:
        async with session_factory() as session:
            await session.execute("SELECT 1")
        return ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Connected",
        )
    except Exception as e:
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )
