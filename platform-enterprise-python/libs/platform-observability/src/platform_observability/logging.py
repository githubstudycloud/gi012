"""Structured Logging Configuration"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def configure_logging(
    level: str = "INFO",
    json_format: bool = True,
    service_name: str = "platform",
    environment: str = "development",
) -> None:
    """
    配置结构化日志

    Args:
        level: 日志级别
        json_format: 是否使用 JSON 格式
        service_name: 服务名称
        environment: 环境名称
    """
    # 标准库日志配置
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # 共享处理器
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # 根据环境选择渲染器
    if json_format:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 配置标准库日志格式化器
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # 应用到所有处理器
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)

    # 添加默认上下文
    structlog.contextvars.bind_contextvars(
        service=service_name,
        environment=environment,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """绑定上下文变量到当前日志"""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """清除上下文变量"""
    structlog.contextvars.clear_contextvars()


class LoggerMixin:
    """日志混入类"""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """获取绑定了类名的日志器"""
        return get_logger(self.__class__.__name__)
