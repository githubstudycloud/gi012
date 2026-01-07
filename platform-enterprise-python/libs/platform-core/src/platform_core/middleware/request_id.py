"""Request ID Middleware"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """请求 ID 中间件 - 为每个请求添加唯一标识"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求头获取或生成新的请求 ID
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # 绑定到 structlog 上下文
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # 存储到 request.state
        request.state.request_id = request_id

        # 处理请求
        response = await call_next(request)

        # 添加响应头
        response.headers[REQUEST_ID_HEADER] = request_id

        # 清除上下文
        structlog.contextvars.unbind_contextvars("request_id")

        return response
