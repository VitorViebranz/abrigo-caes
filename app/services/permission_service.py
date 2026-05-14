from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from daos import PermissionDAO
from schemas import PermissionCreateRequest, PermissionResponse


class PermissionService:
    def __init__(self, db: AsyncSession):
        self._dao = PermissionDAO(db)

    async def get_all(self) -> list[PermissionResponse]:
        permissions = await self._dao.get_all()
        return [PermissionResponse.model_validate(p) for p in permissions]

    async def create(self, request: PermissionCreateRequest) -> PermissionResponse:
        existing = await self._dao.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission '{request.name}' already exists.",
            )
        permission = await self._dao.create(request.name, request.description)
        return PermissionResponse.model_validate(permission)
