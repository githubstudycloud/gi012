"""Base Settings Configuration"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """应用基础配置 - 遵循 12-Factor App"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    APP_NAME: str = "Platform Service"
    APP_ENV: str = Field(
        default="development",
        pattern=r"^(development|staging|production)$",
    )
    DEBUG: bool = False
    SECRET_KEY: str = Field(min_length=32)

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = Field(default=4, ge=1, le=32)

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "json"  # json or console

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.APP_ENV == "development"
