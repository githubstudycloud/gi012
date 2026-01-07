"""Base Repository Pattern"""

from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from platform_db.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """异步仓储基类"""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> ModelT | None:
        """根据 ID 获取"""
        return await self.session.get(self.model, id)

    async def get_by_ids(self, ids: list[int]) -> Sequence[ModelT]:
        """根据 ID 列表获取"""
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelT]:
        """获取所有记录（分页）"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """统计总数"""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, data: dict[str, Any]) -> ModelT:
        """创建记录"""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def create_many(self, data_list: list[dict[str, Any]]) -> list[ModelT]:
        """批量创建"""
        instances = [self.model(**data) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def update(self, instance: ModelT, data: dict[str, Any]) -> ModelT:
        """更新实例"""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update_by_id(self, id: int, data: dict[str, Any]) -> ModelT | None:
        """根据 ID 更新"""
        instance = await self.get_by_id(id)
        if not instance:
            return None
        return await self.update(instance, data)

    async def delete(self, instance: ModelT) -> None:
        """删除实例"""
        await self.session.delete(instance)

    async def delete_by_id(self, id: int) -> bool:
        """根据 ID 删除"""
        instance = await self.get_by_id(id)
        if not instance:
            return False
        await self.delete(instance)
        return True

    async def exists(self, id: int) -> bool:
        """检查是否存在"""
        stmt = select(func.count()).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0
