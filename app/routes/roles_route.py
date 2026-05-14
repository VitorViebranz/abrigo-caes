from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import RoleCreateRequest, RoleUpdateRequest, RoleResponse
from services import RoleService

roles_router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(PermissionChecker("manage_all"))],
)


@roles_router.get(
    "",
    response_model=list[RoleResponse],
    summary="[ADMIN] List all roles",
)
@route_logger
async def get_roles(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)
    return await service.get_all()


@roles_router.post(
    "",
    response_model=RoleResponse,
    status_code=201,
    summary="[ADMIN] Create a role",
)
@route_logger
async def create_role(
    request: Request,
    body: RoleCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)
    return await service.create(body)


@roles_router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    summary="[ADMIN] Update role permissions",
)
@route_logger
async def update_role(
    request: Request,
    role_id: int,
    body: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)
    return await service.update(role_id, body)
