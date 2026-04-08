from fastapi import APIRouter, Depends

from configs import require_volunteer_or_admin
from schemas import VaccineCreateRequest, VaccineUpdateRequest, VaccineResponse, VaccineAlertResponse
from services import VaccineService

vaccines_router = APIRouter(prefix="/vaccines", tags=["Vaccines"])


@vaccines_router.get(
    "/alerts/overdue",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List overdue vaccines",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def get_overdue_vaccines(service: VaccineService = Depends(VaccineService)):
    return service.get_overdue_alerts()


@vaccines_router.get(
    "/alerts/due-soon",
    response_model=list[VaccineAlertResponse],
    summary="[VOLUNTEER/ADMIN] List vaccines due within N days (default 7)",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def get_due_soon_vaccines(
    days: int = 7,
    service: VaccineService = Depends(VaccineService),
):
    return service.get_due_soon_alerts(days=days)


@vaccines_router.get(
    "/dog/{dog_id}",
    response_model=list[VaccineResponse],
    summary="[VOLUNTEER/ADMIN] List all vaccines for a dog",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def get_vaccines_by_dog(dog_id: int, service: VaccineService = Depends(VaccineService)):
    return service.get_by_dog(dog_id)


@vaccines_router.post(
    "",
    response_model=VaccineResponse,
    status_code=201,
    summary="[VOLUNTEER/ADMIN] Register a new vaccine",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def create_vaccine(request: VaccineCreateRequest, service: VaccineService = Depends(VaccineService)):
    return service.create(request)


@vaccines_router.patch(
    "/{vaccine_id}",
    response_model=VaccineResponse,
    summary="[VOLUNTEER/ADMIN] Update a vaccine record",
    dependencies=[Depends(require_volunteer_or_admin)],
)
def update_vaccine(
    vaccine_id: int,
    request: VaccineUpdateRequest,
    service: VaccineService = Depends(VaccineService),
):
    return service.update(vaccine_id, request)
