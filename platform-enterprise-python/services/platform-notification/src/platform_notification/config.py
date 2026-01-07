"""Notification Service Configuration"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """通知服务配置"""

    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATION_",
        env_file=".env",
        extra="ignore",
    )

    # 服务配置
    service_name: str = "platform-notification"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8003

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/platform_notification"
    database_pool_size: int = 10
    database_max_overflow: int = 5

    # Redis 配置
    redis_url: str = "redis://localhost:6379/4"

    # SMTP 配置
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = Field(default="")
    smtp_use_tls: bool = True
    smtp_from_email: str = "noreply@platform.com"
    smtp_from_name: str = "Platform"

    # 模板目录
    template_dir: str = "templates"

    # 可观测性
    otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
