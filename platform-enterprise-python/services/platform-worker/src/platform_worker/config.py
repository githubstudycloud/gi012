"""Worker Service Configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker 服务配置"""

    model_config = SettingsConfigDict(
        env_prefix="WORKER_",
        env_file=".env",
        extra="ignore",
    )

    # 服务配置
    service_name: str = "platform-worker"
    environment: str = "development"
    debug: bool = False

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/platform"
    database_pool_size: int = 10
    database_max_overflow: int = 5

    # Redis 配置
    redis_url: str = "redis://localhost:6379/3"

    # Worker 配置
    consumer_group: str = "platform-workers"
    consumer_name: str = "worker-1"
    batch_size: int = 10
    block_timeout_ms: int = 5000
    domains: list[str] = ["user", "order", "notification"]

    # 可观测性
    otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
