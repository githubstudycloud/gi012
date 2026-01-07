"""User Service Configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """用户服务配置"""

    model_config = SettingsConfigDict(
        env_prefix="USER_",
        env_file=".env",
        extra="ignore",
    )

    # 服务配置
    service_name: str = "platform-user"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8002

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/platform_user"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis 配置
    redis_url: str = "redis://localhost:6379/2"

    # 可观测性
    otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
