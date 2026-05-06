from fastapi import APIRouter, Depends, Request

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
def get_roles(
    request: Request,
    service: RoleService = Depends(RoleService),
):
    return service.get_all()


@roles_router.post(
    "",
    response_model=RoleResponse,
    status_code=201,
    summary="[ADMIN] Create a role",
)
@route_logger
def create_role(
    request: Request,
    body: RoleCreateRequest,
    service: RoleService = Depends(RoleService),
):
    return service.create(body)


@roles_router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    summary="[ADMIN] Update role permissions",
)
@route_logger
def update_role(
    request: Request,
    role_id: int,
    body: RoleUpdateRequest,
    service: RoleService = Depends(RoleService),
):
    return service.update(role_id, body)
