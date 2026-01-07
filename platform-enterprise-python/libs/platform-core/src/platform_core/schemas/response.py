"""Response Schemas"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    """响应元数据"""

    request_id: str = Field(description="请求唯一标识")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    version: str = Field(default="1.0", description="API 版本")


class ErrorResponse(BaseModel):
    """错误响应"""

    code: str = Field(description="错误代码")
    message: str = Field(description="错误消息")
    details: dict[str, Any] = Field(default_factory=dict, description="错误详情")


class ApiResponse(BaseModel, Generic[DataT]):
    """统一 API 响应格式"""

    success: bool = Field(default=True, description="请求是否成功")
    data: DataT | None = Field(default=None, description="响应数据")
    error: ErrorResponse | None = Field(default=None, description="错误信息")
    meta: ResponseMeta | None = Field(default=None, description="元数据")

    @classmethod
    def ok(cls, data: DataT, meta: ResponseMeta | None = None) -> "ApiResponse[DataT]":
        """成功响应"""
        return cls(success=True, data=data, meta=meta)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        meta: ResponseMeta | None = None,
    ) -> "ApiResponse[None]":
        """失败响应"""
        return cls(
            success=False,
            error=ErrorResponse(code=code, message=message, details=details or {}),
            meta=meta,
        )
