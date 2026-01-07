"""Platform Auth Service - Main Application"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from platform_core.exceptions import PlatformException
from platform_core.middleware import RequestIdMiddleware, TimingMiddleware
from platform_core.schemas import ErrorResponse
from platform_db import DatabaseManager
from platform_observability import configure_logging, configure_tracing

from platform_auth.config import settings
from platform_auth.routers import router


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

    # 初始化数据库
    app.state.db_manager = DatabaseManager(
        url=settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )

    # 初始化 Redis
    app.state.redis = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    yield

    # 清理资源
    await app.state.redis.close()
    await app.state.db_manager.close()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Platform Auth Service",
        description="认证和授权服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # 添加中间件
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TimingMiddleware)

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

    # 健康检查
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": settings.service_name}

    # 注册路由
    app.include_router(router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "platform_auth.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
