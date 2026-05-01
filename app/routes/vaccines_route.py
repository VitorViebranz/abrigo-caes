from fastapi import APIRouter, Depends, Request

from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import VaccineCreateRequest, VaccineUpdateRequest, VaccineResponse, VaccineAlertResponse
from services import VaccineService

vaccines_router = APIRouter(
    prefix="/vaccines",
    tags=["Vaccines"],
    dependencies=[Depends(PermissionChecker("manage_dogs"))],
)

@vaccines_router.get(
    "/alerts/overdue",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List overdue vaccines",
)
@route_logger
def get_overdue_vaccines(request: Request, service: VaccineService = Depends(VaccineService)):
    return service.get_overdue_alerts()

@vaccines_router.get(
    "/alerts/due-soon",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List vaccines due within N days (default 7)",
)
@route_logger
def get_due_soon_vaccines(
    request: Request,
    days: int = 7,
    service: VaccineService = Depends(VaccineService),
):
    return service.get_due_soon_alerts(days=days)

@vaccines_router.get(
    "/dog/{dog_id}",
    response_model=list[VaccineResponse],
    summary="[VOLUNTEER/ADMIN] List all vaccines for a dog",
)
@route_logger
def get_vaccines_by_dog(
    request: Request,
    dog_id: int,
    service: VaccineService = Depends(VaccineService),
):
    return service.get_by_dog(dog_id)

@vaccines_router.post(
    "",
    response_model=VaccineResponse,
    status_code=201,
    summary="[VOLUNTEER/ADMIN] Register a new vaccine",
)
@route_logger
def create_vaccine(
    request: Request,
    body: VaccineCreateRequest,
    service: VaccineService = Depends(VaccineService),
):
    return service.create(body)

@vaccines_router.patch(
    "/{vaccine_id}",
    response_model=VaccineResponse,
    summary="[VOLUNTEER/ADMIN] Update a vaccine record",
)
@route_logger
def update_vaccine(
    request: Request,
    vaccine_id: int,
    body: VaccineUpdateRequest,
    service: VaccineService = Depends(VaccineService),
):
    return service.update(vaccine_id, body)

@vaccines_router.delete(
    "/{vaccine_id}",
    summary="[VOLUNTEER/ADMIN] Deactivate a vaccine record (soft delete)",
)
@route_logger
def deactivate_vaccine(
    request: Request,
    vaccine_id: int,
    service: VaccineService = Depends(VaccineService),
):
    return service.deactivate(vaccine_id)