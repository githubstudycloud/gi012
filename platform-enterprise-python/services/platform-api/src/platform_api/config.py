"""API Gateway Configuration"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API 网关配置"""

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        extra="ignore",
    )

    # 服务配置
    service_name: str = "platform-api"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # 后端服务地址
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # JWT 配置
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"

    # 限流配置
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # CORS 配置
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # 可观测性
    otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
