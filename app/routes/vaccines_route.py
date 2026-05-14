from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import VaccineCreateRequest, VaccineUpdateRequest, VaccineResponse, VaccineAlertResponse
from services import VaccineService

vaccines_router = APIRouter(
    prefix="/vaccines",
    tags=["Vaccines"],
    dependencies=[Depends(PermissionChecker("manage_animals"))],
)

@vaccines_router.get(
    "/alerts/overdue",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List overdue vaccines",
)
@route_logger
async def get_overdue_vaccines(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.get_overdue_alerts()

@vaccines_router.get(
    "/alerts/due-soon",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List vaccines due within N days (default 7)",
)
@route_logger
async def get_due_soon_vaccines(
    request: Request,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.get_due_soon_alerts(days=days)

@vaccines_router.get(
    "/animal/{animal_id}",
    response_model=list[VaccineResponse],
    summary="[VOLUNTEER/ADMIN] List all vaccines for an animal",
)
@route_logger
async def get_vaccines_by_animal(
    request: Request,
    animal_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.get_by_animal(animal_id)

@vaccines_router.post(
    "",
    response_model=VaccineResponse,
    status_code=201,
    summary="[VOLUNTEER/ADMIN] Register a new vaccine",
)
@route_logger
async def create_vaccine(
    request: Request,
    body: VaccineCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.create(body)

@vaccines_router.patch(
    "/{vaccine_id}",
    response_model=VaccineResponse,
    summary="[VOLUNTEER/ADMIN] Update a vaccine record",
)
@route_logger
async def update_vaccine(
    request: Request,
    vaccine_id: int,
    body: VaccineUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.update(vaccine_id, body)

@vaccines_router.delete(
    "/{vaccine_id}",
    summary="[VOLUNTEER/ADMIN] Deactivate a vaccine record (soft delete)",
)
@route_logger
async def deactivate_vaccine(
    request: Request,
    vaccine_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = VaccineService(db)
    return await service.deactivate(vaccine_id)