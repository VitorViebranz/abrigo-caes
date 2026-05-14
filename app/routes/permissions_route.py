from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import PermissionCreateRequest, PermissionResponse
from services import PermissionService

permissions_router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[Depends(PermissionChecker("manage_all"))],
)


@permissions_router.get(
    "",
    response_model=list[PermissionResponse],
    summary="[ADMIN] List all permissions",
)
@route_logger
async def get_permissions(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(db)
    return await service.get_all()


@permissions_router.post(
    "",
    response_model=PermissionResponse,
    status_code=201,
    summary="[ADMIN] Create a permission",
)
@route_logger
async def create_permission(
    request: Request,
    body: PermissionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(db)
    return await service.create(body)
