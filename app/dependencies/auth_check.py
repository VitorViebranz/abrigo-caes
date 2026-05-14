from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from configs import get_db
from configs.security import verify_token
from models import RoleModel


async def get_user_permissions(
    current_user = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    if not current_user or not getattr(current_user, "role_id", None):
        return []

    stmt = (
        select(RoleModel)
        .options(selectinload(RoleModel.permissions))
        .where(RoleModel.id == current_user.role_id)
    )
    result = await db.execute(stmt)
    role = result.unique().scalar_one_or_none()
    if not role:
        return []
    return [p.name for p in role.permissions]


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self,
        current_user = Depends(verify_token),
        db: AsyncSession = Depends(get_db),
    ):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        if not getattr(current_user, "role_id", None):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        stmt = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(RoleModel.id == current_user.role_id)
        )
        result = await db.execute(stmt)
        role = result.unique().scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not found.")

        user_permissions = [p.name for p in role.permissions]

        if "manage_all" not in user_permissions and self.required_permission not in user_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return current_user
