"""Auth Service Configuration"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """认证服务配置"""

    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        extra="ignore",
    )

    # 服务配置
    service_name: str = "platform-auth"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/platform_auth"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis 配置
    redis_url: str = "redis://localhost:6379/1"

    # JWT 配置
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 密码配置
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_number: bool = True

    # 可观测性
    otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
