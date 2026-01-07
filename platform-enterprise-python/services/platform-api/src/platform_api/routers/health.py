"""Health Check Endpoints"""

from fastapi import APIRouter

from platform_observability import HealthCheck, HealthStatus

router = APIRouter()

health_check = HealthCheck(service_name="platform-api", version="1.0.0")


@router.get("/health")
async def health() -> dict:
    """存活检查"""
    return await health_check.liveness()


@router.get("/health/ready")
async def readiness() -> dict:
    """就绪检查"""
    report = await health_check.readiness()
    return report.to_dict()
