from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import (
    AnimalCreateForm,
    AnimalUpdateRequest,
    AnimalStatusUpdateRequest,
    AnimalResponse,
    AnimalListResponse,
    PaginationParams,
)
from services import AnimalService

animals_router = APIRouter(prefix="/animals", tags=["Animals"])


@animals_router.get(
    "",
    response_model=AnimalListResponse,
    summary="List all active animals"
)
@route_logger
async def get_all_animals(
    request: Request,
    include_inactive: bool = False,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    return await service.get_all(
        include_inactive=include_inactive,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@animals_router.get(
    "/{animal_id}",
    response_model=AnimalResponse,
    summary="Get an animal by ID"
)
@route_logger
async def get_animal(
    request: Request,
    animal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    return await service.get_by_id(animal_id)


@animals_router.post(
    "",
    response_model=AnimalResponse,
    status_code=201,
    summary="[FUNCIONARIO/ADMIN] Register a new animal"
)
@route_logger
async def create_animal(
    request: Request,
    animal_form: AnimalCreateForm = Depends(AnimalCreateForm.as_form),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    animal = await service.create(animal_form.to_request())
    if image:
        return await service.set_image(animal.id, image)
    return animal


@animals_router.patch(
    "/{animal_id}",
    summary="[FUNCIONARIO/ADMIN] Update animal details"
)
@route_logger
async def update_animal(
    request: Request,
    animal_id: int,
    animal_update: AnimalUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    return await service.update(animal_id, animal_update)


@animals_router.patch(
    "/{animal_id}/status",
    summary="[FUNCIONARIO/ADMIN] Update adoption status (rules enforced)"
)
@route_logger
async def update_animal_status(
    request: Request,
    animal_id: int,
    animal_status_update: AnimalStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    return await service.update_status(animal_id, animal_status_update)


@animals_router.delete(
    "/{animal_id}",
    summary="[FUNCIONARIO/ADMIN] Deactivate an animal (soft delete)"
)
@route_logger
async def deactivate_animal(
    request: Request,
    animal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals"))
):
    service = AnimalService(db)
    return await service.deactivate(animal_id)


@animals_router.post(
    "/{animal_id}/image",
    response_model=AnimalResponse,
    summary="[FUNCIONARIO/ADMIN] Upload or replace animal image",
)
@route_logger
async def upload_animal_image(
    request: Request,
    animal_id: int,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(PermissionChecker("manage_animals")),
):
    service = AnimalService(db)
    return await service.set_image(animal_id, image)