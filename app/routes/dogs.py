from fastapi import APIRouter, Depends

from configs import require_admin, require_volunteer_or_admin
from schemas import DogCreateRequest, DogUpdateRequest, DogStatusUpdateRequest, DogResponse
from services import DogService

dogs_router = APIRouter(prefix="/dogs", tags=["Dogs"])


@dogs_router.get(
    "",
    response_model=list[DogResponse],
    summary="List all active dogs",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def get_all_dogs(
    include_inactive: bool = False,
    service: DogService = Depends(DogService),
):
    return service.get_all(include_inactive=include_inactive)


@dogs_router.get(
    "/{dog_id}",
    response_model=DogResponse,
    summary="Get a dog by ID",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def get_dog(dog_id: int, service: DogService = Depends(DogService)):
    return service.get_by_id(dog_id)


@dogs_router.post(
    "",
    response_model=DogResponse,
    status_code=201,
    summary="[VOLUNTEER/ADMIN] Register a new dog",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def create_dog(request: DogCreateRequest, service: DogService = Depends(DogService)):
    return service.create(request)


@dogs_router.patch(
    "/{dog_id}",
    response_model=DogResponse,
    summary="[VOLUNTEER/ADMIN] Update dog details",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def update_dog(dog_id: int, request: DogUpdateRequest, service: DogService = Depends(DogService)):
    return service.update(dog_id, request)


@dogs_router.patch(
    "/{dog_id}/status",
    response_model=DogResponse,
    summary="[VOLUNTEER/ADMIN] Update adoption status (rules enforced)",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def update_dog_status(
    dog_id: int,
    request: DogStatusUpdateRequest,
    service: DogService = Depends(DogService),
):
    return service.update_status(dog_id, request)


@dogs_router.delete(
    "/{dog_id}",
    summary="[ADMIN] Deactivate a dog (soft delete)",
    dependencies=[Depends(require_admin)],
)
def deactivate_dog(dog_id: int, service: DogService = Depends(DogService)):
    return service.deactivate(dog_id)
