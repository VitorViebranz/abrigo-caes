from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse, PaginationParams
from services import UserService

users_router = APIRouter(
    prefix="/users", 
    tags=["Users"],
    dependencies=[Depends(PermissionChecker("manage_all"))]
)

@users_router.get(
    "",
    response_model=UserListResponse,
    summary="[ADMIN] List all users"
)
@route_logger
async def get_all_users(
    request: Request,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_all(page=pagination.page, page_size=pagination.page_size)

@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Get a user by ID"
)
@route_logger
async def get_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_by_id(user_id)

@users_router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="[ADMIN] Create a new user"
)
@route_logger
async def create_user(
    request: Request,
    body: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.create(body)

@users_router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Update user details"
)
@route_logger
async def update_user(
    request: Request,
    user_id: int,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update(user_id, body)

@users_router.patch(
    "/{user_id}/deactivate",
    summary="[ADMIN] Deactivate a user"
)
@route_logger
async def deactivate_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.deactivate(user_id)

@users_router.patch(
    "/{user_id}/activate",
    summary="[ADMIN] Reactivate a user"
)
@route_logger
async def activate_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.activate(user_id)