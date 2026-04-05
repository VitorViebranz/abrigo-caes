from fastapi import APIRouter, Depends

from configs import require_admin
from schemas import UserCreateRequest, UserResponse
from services import UserService

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get(
    "",
    response_model=list[UserResponse],
    summary="[ADMIN] List all users",
    dependencies=[Depends(require_admin)],
)
def get_all_users(service: UserService = Depends(UserService)):
    return service.get_all()


@users_router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="[ADMIN] Create a new user",
    dependencies=[Depends(require_admin)],
)
def create_user(request: UserCreateRequest, service: UserService = Depends(UserService)):
    return service.create(request)


@users_router.patch(
    "/{user_id}/deactivate",
    summary="[ADMIN] Deactivate a user",
    dependencies=[Depends(require_admin)],
)
def deactivate_user(user_id: int, service: UserService = Depends(UserService)):
    return service.deactivate(user_id)


@users_router.patch(
    "/{user_id}/activate",
    summary="[ADMIN] Reactivate a user",
    dependencies=[Depends(require_admin)],
)
def activate_user(user_id: int, service: UserService = Depends(UserService)):
    return service.activate(user_id)
