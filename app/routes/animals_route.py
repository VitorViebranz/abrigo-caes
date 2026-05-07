import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from configs.decorators import route_logger
from configs.security import verify_token
from dependencies import PermissionChecker
from schemas import AnimalCreateRequest, AnimalUpdateRequest, AnimalStatusUpdateRequest, AnimalResponse
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
    name: str = Form(...),
    estimated_age: float = Form(...),
    size: str = Form(...),
    species: str = Form(...),
    entry_date: str = Form(...),
    notes: str | None = Form(None),
    neutered: bool = Form(False),
    dewormed: bool = Form(False),
    socializes_with_other_animals: bool = Form(False),
    color: str | None = Form(None),
    microchipped: bool = Form(False),
    vaccines: str | None = Form(None),
    image: UploadFile | None = File(None),
    service: AnimalService = Depends(AnimalService),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    vaccine_items: list[dict] = []
    if vaccines:
        try:
            parsed = json.loads(vaccines)
            if isinstance(parsed, list):
                vaccine_items = parsed
            else:
                raise ValueError("vaccines must be a list")
        except (ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid vaccines payload: {exc}",
            )

    animal_create = AnimalCreateRequest.model_validate({
        "name": name,
        "estimated_age": estimated_age,
        "size": size,
        "species": species,
        "entry_date": entry_date,
        "notes": notes,
        "neutered": neutered,
        "dewormed": dewormed,
        "socializes_with_other_animals": socializes_with_other_animals,
        "color": color,
        "microchipped": microchipped,
        "vaccines": vaccine_items,
    })

    animal = service.create(animal_create)
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