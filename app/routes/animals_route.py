from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import AnimalCreateForm, AnimalUpdateRequest, AnimalStatusUpdateRequest, AnimalResponse
from services import AnimalService

animals_router = APIRouter(prefix="/animals", tags=["Animals"])


@animals_router.get(
    "",
    response_model=list[AnimalResponse],
    summary="List all active animals"
)
@route_logger
def get_all_animals(
    request: Request,
    include_inactive: bool = False,
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    return service.get_all(include_inactive=include_inactive)


@animals_router.get(
    "/{animal_id}",
    response_model=AnimalResponse,
    summary="Get an animal by ID"
)
@route_logger
def get_animal(
    request: Request,
    animal_id: int,
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    return service.get_by_id(animal_id)


@animals_router.post(
    "",
    response_model=AnimalResponse,
    status_code=201,
    summary="[FUNCIONARIO/ADMIN] Register a new animal"
)
@route_logger
def create_animal(
    request: Request,
    animal_form: AnimalCreateForm = Depends(AnimalCreateForm.as_form),
    image: UploadFile = File(...),
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    animal = service.create(animal_form.to_request())
    if image:
        return service.set_image(animal.id, image)
    return animal


@animals_router.patch(
    "/{animal_id}",
    summary="[FUNCIONARIO/ADMIN] Update animal details"
)
@route_logger
def update_animal(
    request: Request,
    animal_id: int,
    animal_update: AnimalUpdateRequest,
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    return service.update(animal_id, animal_update)


@animals_router.patch(
    "/{animal_id}/status",
    summary="[FUNCIONARIO/ADMIN] Update adoption status (rules enforced)"
)
@route_logger
def update_animal_status(
    request: Request,
    animal_id: int,
    animal_status_update: AnimalStatusUpdateRequest,
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    return service.update_status(animal_id, animal_status_update)


@animals_router.delete(
    "/{animal_id}",
    summary="[FUNCIONARIO/ADMIN] Deactivate an animal (soft delete)"
)
@route_logger
def deactivate_animal(
    request: Request,
    animal_id: int,
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    return service.deactivate(animal_id)


@animals_router.post(
    "/{animal_id}/image",
    response_model=AnimalResponse,
    summary="[FUNCIONARIO/ADMIN] Upload or replace animal image",
)
@route_logger
def upload_animal_image(
    request: Request,
    animal_id: int,
    image: UploadFile = File(...),
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals")),
):
    return service.set_image(animal_id, image)