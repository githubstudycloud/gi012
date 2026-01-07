"""OpenTelemetry Tracing Configuration"""

from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Span, SpanKind, Tracer


def configure_tracing(
    service_name: str,
    environment: str = "development",
    otlp_endpoint: str | None = None,
    console_export: bool = False,
) -> TracerProvider:
    """
    配置 OpenTelemetry 追踪

    Args:
        service_name: 服务名称
        environment: 环境名称
        otlp_endpoint: OTLP 导出端点
        console_export: 是否输出到控制台

    Returns:
        TracerProvider 实例
    """
    # 创建资源
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": environment,
        }
    )

    # 创建 TracerProvider
    provider = TracerProvider(resource=resource)

    # 配置导出器
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    if console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # 设置全局 TracerProvider
    trace.set_tracer_provider(provider)

    return provider


def get_tracer(name: str = "platform") -> Tracer:
    """获取 Tracer 实例"""
    return trace.get_tracer(name)


def instrument_fastapi(app: Any) -> None:
    """为 FastAPI 应用添加追踪"""
    FastAPIInstrumentor.instrument_app(app)


def instrument_httpx() -> None:
    """为 HTTPX 客户端添加追踪"""
    HTTPXClientInstrumentor().instrument()


def instrument_sqlalchemy(engine: Any) -> None:
    """为 SQLAlchemy 添加追踪"""
    SQLAlchemyInstrumentor().instrument(engine=engine)


def instrument_redis() -> None:
    """为 Redis 客户端添加追踪"""
    RedisInstrumentor().instrument()


def create_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: dict[str, Any] | None = None,
) -> Span:
    """创建新的 Span"""
    tracer = get_tracer()
    return tracer.start_span(name, kind=kind, attributes=attributes)


class TracingMiddleware:
    """追踪中间件辅助类"""

    def __init__(self, tracer: Tracer | None = None) -> None:
        self.tracer = tracer or get_tracer()

    def trace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
    ) -> Any:
        """装饰器：为函数添加追踪"""

        def decorator(func: Any) -> Any:
            import functools

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.tracer.start_as_current_span(name, kind=kind):
                    return await func(*args, **kwargs)

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.tracer.start_as_current_span(name, kind=kind):
                    return func(*args, **kwargs)

            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator
