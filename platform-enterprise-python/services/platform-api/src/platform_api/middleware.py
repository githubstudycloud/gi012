"""API Gateway Middleware"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from platform_cache import CacheClient, RateLimiter
from platform_core.exceptions import RateLimitError
from platform_observability import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(
        self,
        app,
        cache: CacheClient,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.limiter = RateLimiter(cache)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        # 跳过健康检查端点
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # 获取客户端标识
        client_ip = request.client.host if request.client else "unknown"
        key = f"ip:{client_ip}"

        # 检查限流
        allowed, remaining, reset = await self.limiter.is_allowed(
            key, self.max_requests, self.window_seconds
        )

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                extra={"client_ip": client_ip, "reset_seconds": reset},
            )
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {reset} seconds"
            )

        # 添加限流响应头
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        import time

        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host if request.client else None,
            },
        )

        return response
