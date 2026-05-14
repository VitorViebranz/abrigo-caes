from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import RoleModel, PermissionModel, role_permissions


class RoleDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[RoleModel]:
        stmt = select(RoleModel).options(selectinload(RoleModel.permissions)).order_by(RoleModel.name.asc())
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_name(self, name: str) -> RoleModel | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, role_id: int) -> RoleModel | None:
        stmt = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(RoleModel.id == role_id)
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, name: str) -> RoleModel:
        stmt = insert(RoleModel).values(name=name)
        await self._session.execute(stmt)
        return await self.get_by_name(name)

    async def set_permissions(self, role_id: int, permission_ids: list[int]) -> None:
        await self._session.execute(
            delete(role_permissions).where(role_permissions.c.role_id == role_id)
        )
        if permission_ids:
            await self._session.execute(
                insert(role_permissions).values(
                    [
                        {"role_id": role_id, "permission_id": pid}
                        for pid in permission_ids
                    ]
                )
            )

    async def get_permissions_by_role(self, role_id: int) -> list[PermissionModel]:
        stmt = (
            select(PermissionModel)
            .join(role_permissions, PermissionModel.id == role_permissions.c.permission_id)
            .where(role_permissions.c.role_id == role_id)
            .order_by(PermissionModel.name.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
