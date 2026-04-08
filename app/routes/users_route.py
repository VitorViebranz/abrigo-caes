from fastapi import APIRouter, Depends

from configs.security import verify_token
from schemas import UserCreateRequest, UserResponse
from services import UserService

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get(
    "",
    response_model=list[UserResponse],
    summary="[ADMIN] List all users"
)
def get_all_users(
    service: UserService = Depends(UserService),
    current_user: dict = Depends(verify_token)
):
    return service.get_all()


@users_router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="[ADMIN] Create a new user"
)
def create_user(
    request: UserCreateRequest, 
    service: UserService = Depends(UserService), 
    current_user: dict = Depends(verify_token)
):
    return service.create(request)


@users_router.patch(
    "/{user_id}/deactivate",
    summary="[ADMIN] Deactivate a user"
)
def deactivate_user(
    user_id: int, 
    service: UserService = Depends(UserService), 
    current_user: dict = Depends(verify_token)
):
    return service.deactivate(user_id)


@users_router.patch(
    "/{user_id}/activate",
    summary="[ADMIN] Reactivate a user"
)
def activate_user(
    user_id: int, 
    service: UserService = Depends(UserService), 
    current_user: dict = Depends(verify_token)
):
    return service.activate(user_id)