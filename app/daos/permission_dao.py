from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from models import PermissionModel


class PermissionDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[PermissionModel]:
        stmt = select(PermissionModel).order_by(PermissionModel.name.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_name(self, name: str) -> PermissionModel | None:
        stmt = select(PermissionModel).where(PermissionModel.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, name: str, description: str | None = None) -> PermissionModel:
        stmt = insert(PermissionModel).values(name=name, description=description)
        await self._session.execute(stmt)
        return await self.get_by_name(name)
