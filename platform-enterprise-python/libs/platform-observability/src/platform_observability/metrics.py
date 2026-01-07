"""Prometheus Metrics"""

from typing import Any

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter as PrometheusCounter,
    Gauge as PrometheusGauge,
    Histogram as PrometheusHistogram,
    generate_latest,
)


class Counter:
    """计数器指标"""

    def __init__(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        registry: CollectorRegistry | None = None,
    ) -> None:
        self._counter = PrometheusCounter(
            name,
            description,
            labels or [],
            registry=registry or REGISTRY,
        )
        self._labels = labels or []

    def inc(self, value: float = 1, **labels: str) -> None:
        """增加计数"""
        if labels:
            self._counter.labels(**labels).inc(value)
        else:
            self._counter.inc(value)


class Histogram:
    """直方图指标"""

    DEFAULT_BUCKETS = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    )

    def __init__(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
        registry: CollectorRegistry | None = None,
    ) -> None:
        self._histogram = PrometheusHistogram(
            name,
            description,
            labels or [],
            buckets=buckets or self.DEFAULT_BUCKETS,
            registry=registry or REGISTRY,
        )
        self._labels = labels or []

    def observe(self, value: float, **labels: str) -> None:
        """记录观测值"""
        if labels:
            self._histogram.labels(**labels).observe(value)
        else:
            self._histogram.observe(value)

    def time(self, **labels: str) -> Any:
        """计时上下文管理器"""
        if labels:
            return self._histogram.labels(**labels).time()
        return self._histogram.time()


class Gauge:
    """仪表盘指标"""

    def __init__(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        registry: CollectorRegistry | None = None,
    ) -> None:
        self._gauge = PrometheusGauge(
            name,
            description,
            labels or [],
            registry=registry or REGISTRY,
        )
        self._labels = labels or []

    def set(self, value: float, **labels: str) -> None:
        """设置值"""
        if labels:
            self._gauge.labels(**labels).set(value)
        else:
            self._gauge.set(value)

    def inc(self, value: float = 1, **labels: str) -> None:
        """增加"""
        if labels:
            self._gauge.labels(**labels).inc(value)
        else:
            self._gauge.inc(value)

    def dec(self, value: float = 1, **labels: str) -> None:
        """减少"""
        if labels:
            self._gauge.labels(**labels).dec(value)
        else:
            self._gauge.dec(value)


class MetricsRegistry:
    """指标注册表"""

    def __init__(self, prefix: str = "platform") -> None:
        self.prefix = prefix
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._gauges: dict[str, Gauge] = {}

    def _make_name(self, name: str) -> str:
        """生成完整指标名"""
        return f"{self.prefix}_{name}"

    def counter(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
    ) -> Counter:
        """获取或创建计数器"""
        full_name = self._make_name(name)
        if full_name not in self._counters:
            self._counters[full_name] = Counter(full_name, description, labels)
        return self._counters[full_name]

    def histogram(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: tuple[float, ...] | None = None,
    ) -> Histogram:
        """获取或创建直方图"""
        full_name = self._make_name(name)
        if full_name not in self._histograms:
            self._histograms[full_name] = Histogram(
                full_name, description, labels, buckets
            )
        return self._histograms[full_name]

    def gauge(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
    ) -> Gauge:
        """获取或创建仪表盘"""
        full_name = self._make_name(name)
        if full_name not in self._gauges:
            self._gauges[full_name] = Gauge(full_name, description, labels)
        return self._gauges[full_name]

    @staticmethod
    def export() -> bytes:
        """导出指标为 Prometheus 格式"""
        return generate_latest(REGISTRY)


# 全局默认注册表
default_registry = MetricsRegistry()


# 预定义的常用指标
http_requests_total = default_registry.counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = default_registry.histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_connections = default_registry.gauge(
    "active_connections",
    "Number of active connections",
    ["type"],
)
