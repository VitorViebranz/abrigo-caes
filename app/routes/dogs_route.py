from fastapi import APIRouter, Depends, Request

from configs.decorators import route_logger
from configs.security import verify_token
from schemas import DogCreateRequest, DogUpdateRequest, DogStatusUpdateRequest, DogResponse
from services import DogService

dogs_router = APIRouter(prefix="/dogs", tags=["Dogs"])


@dogs_router.get(
    "",
    response_model=list[DogResponse],
    summary="List all active dogs"
)
@route_logger
def get_all_dogs(
    request: Request,
    include_inactive: bool = False,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.get_all(include_inactive=include_inactive)


@dogs_router.get(
    "/{dog_id}",
    response_model=DogResponse,
    summary="Get a dog by ID"
)
@route_logger
def get_dog(
    request: Request,
    dog_id: int, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.get_by_id(dog_id)


@dogs_router.post(
    "",
    status_code=201,
    summary="[FUNCIONARIO/ADMIN] Register a new dog"
)
@route_logger
def create_dog(
    request: Request,
    dog_create: DogCreateRequest, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.create(dog_create)


@dogs_router.patch(
    "/{dog_id}",
    summary="[FUNCIONARIO/ADMIN] Update dog details"
)
@route_logger
def update_dog(
    request: Request,
    dog_id: int, 
    dog_update: DogUpdateRequest, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.update(dog_id, dog_update)


@dogs_router.patch(
    "/{dog_id}/status",
    summary="[FUNCIONARIO/ADMIN] Update adoption status (rules enforced)"
)
@route_logger
def update_dog_status(
    request: Request,
    dog_id: int,
    dog_status_update: DogStatusUpdateRequest,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.update_status(dog_id, dog_status_update)


@dogs_router.delete(
    "/{dog_id}",
    summary="[FUNCIONARIO/ADMIN] Deactivate a dog (soft delete)"
)
@route_logger
def deactivate_dog(
    request: Request,
    dog_id: int,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.deactivate(dog_id)
