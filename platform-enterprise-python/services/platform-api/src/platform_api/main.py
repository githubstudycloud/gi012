"""Platform API Gateway - Main Application"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from platform_cache import CacheClient
from platform_core.exceptions import PlatformException
from platform_core.middleware import RequestIdMiddleware, TimingMiddleware
from platform_core.schemas import ErrorResponse
from platform_observability import configure_logging, configure_tracing

from platform_api.config import settings
from platform_api.middleware import LoggingMiddleware
from platform_api.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 配置日志
    configure_logging(
        level=settings.log_level,
        json_format=settings.log_json,
        service_name=settings.service_name,
        environment=settings.environment,
    )

    # 配置追踪
    if settings.otlp_endpoint:
        configure_tracing(
            service_name=settings.service_name,
            environment=settings.environment,
            otlp_endpoint=settings.otlp_endpoint,
        )

    # 初始化 Redis
    app.state.redis = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    # 初始化 HTTP 客户端
    app.state.http_client = httpx.AsyncClient(timeout=30.0)

    # 初始化缓存
    app.state.cache = CacheClient(app.state.redis, prefix="api")

    yield

    # 清理资源
    await app.state.http_client.aclose()
    await app.state.redis.close()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Platform API Gateway",
        description="统一 API 网关",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # 添加中间件 (顺序重要)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)

    # 异常处理器
    @app.exception_handler(PlatformException)
    async def platform_exception_handler(
        request: Request, exc: PlatformException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.error_code,
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            ).model_dump(),
        )

    # 注册路由
    app.include_router(api_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "platform_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
