"""Base Schema"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """基础 Schema 配置"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        validate_default=True,
        from_attributes=True,
        populate_by_name=True,
    )
