"""API Routers"""

from fastapi import APIRouter

from platform_api.routers import health, proxy

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, tags=["Health"])

# 代理路由
api_router.include_router(proxy.router, prefix="/v1", tags=["Proxy"])
