from fastapi import APIRouter, Depends, Request

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
def get_permissions(
    request: Request,
    service: PermissionService = Depends(PermissionService),
):
    return service.get_all()


@permissions_router.post(
    "",
    response_model=PermissionResponse,
    status_code=201,
    summary="[ADMIN] Create a permission",
)
@route_logger
def create_permission(
    request: Request,
    body: PermissionCreateRequest,
    service: PermissionService = Depends(PermissionService),
):
    return service.create(body)
