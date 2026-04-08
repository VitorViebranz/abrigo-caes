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
@route_logger()
def get_all_dogs(
    request: Request,
    include_inactive: bool = False,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.get_all(include_inactive=include_inactive)


@route_logger()
@dogs_router.get(
    "/{dog_id}",
    response_model=DogResponse,
    summary="Get a dog by ID"
)
def get_dog(
    dog_id: int, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.get_by_id(dog_id)


@route_logger()
@dogs_router.post(
    "",
    response_model=DogResponse,
    status_code=201,
    summary="[VOLUNTEER/ADMIN] Register a new dog"
)
def create_dog(
    request: DogCreateRequest, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.create(request)


@route_logger()
@dogs_router.patch(
    "/{dog_id}",
    response_model=DogResponse,
    summary="[VOLUNTEER/ADMIN] Update dog details"
)
def update_dog(
    dog_id: int, 
    request: DogUpdateRequest, 
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.update(dog_id, request)


@route_logger()
@dogs_router.patch(
    "/{dog_id}/status",
    response_model=DogResponse,
    summary="[VOLUNTEER/ADMIN] Update adoption status (rules enforced)"
)
def update_dog_status(
    dog_id: int,
    request: DogStatusUpdateRequest,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.update_status(dog_id, request)


@route_logger()
@dogs_router.delete(
    "/{dog_id}",
    summary="[ADMIN] Deactivate a dog (soft delete)"
)
def deactivate_dog(
    dog_id: int,
    service: DogService = Depends(DogService),
    current_user: dict = Depends(verify_token)
):
    return service.deactivate(dog_id)
