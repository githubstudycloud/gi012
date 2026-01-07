"""Platform Observability - 日志、指标、追踪"""

from platform_observability.logging import configure_logging, get_logger
from platform_observability.metrics import MetricsRegistry, Counter, Histogram, Gauge
from platform_observability.tracing import configure_tracing, get_tracer
from platform_observability.health import HealthCheck, HealthStatus

__version__ = "1.0.0"

__all__ = [
    "configure_logging",
    "get_logger",
    "MetricsRegistry",
    "Counter",
    "Histogram",
    "Gauge",
    "configure_tracing",
    "get_tracer",
    "HealthCheck",
    "HealthStatus",
]
