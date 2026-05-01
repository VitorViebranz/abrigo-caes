from fastapi import APIRouter, Depends, Request

from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import UserCreateRequest, UserUpdateRequest, UserResponse
from services import UserService

users_router = APIRouter(
    prefix="/users", 
    tags=["Users"],
    dependencies=[Depends(PermissionChecker("manage_all"))]
)

@users_router.get(
    "",
    response_model=list[UserResponse],
    summary="[ADMIN] List all users"
)
@route_logger
def get_all_users(
    request: Request,
    service: UserService = Depends(UserService)
):
    return service.get_all()

@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Get a user by ID"
)
@route_logger
def get_user(
    request: Request,
    user_id: int,
    service: UserService = Depends(UserService)
):
    return service.get_by_id(user_id)

@users_router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="[ADMIN] Create a new user"
)
@route_logger
def create_user(
    request: Request,
    body: UserCreateRequest,
    service: UserService = Depends(UserService)
):
    return service.create(body)

@users_router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Update user details"
)
@route_logger
def update_user(
    request: Request,
    user_id: int,
    body: UserUpdateRequest,
    service: UserService = Depends(UserService)
):
    return service.update(user_id, body)

@users_router.patch(
    "/{user_id}/deactivate",
    summary="[ADMIN] Deactivate a user"
)
@route_logger
def deactivate_user(
    request: Request,
    user_id: int,
    service: UserService = Depends(UserService)
):
    return service.deactivate(user_id)

@users_router.patch(
    "/{user_id}/activate",
    summary="[ADMIN] Reactivate a user"
)
@route_logger
def activate_user(
    request: Request,
    user_id: int,
    service: UserService = Depends(UserService)
):
    return service.activate(user_id)