from fastapi import APIRouter, Depends, Request

from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import DonationCreateRequest, DonationResponse
from services import DonationService


donations_router = APIRouter(
    prefix="/donations",
    tags=["Donations"],
    dependencies=[Depends(PermissionChecker("manage_finances"))],
)


@donations_router.get(
    "",
    response_model=list[DonationResponse],
    summary="[FINANCIAL/ADMIN] List donations",
)
@route_logger
def list_donations(
    request: Request,
    service: DonationService = Depends(DonationService),
):
    return service.get_all()


@donations_router.get(
    "/{donation_id}",
    response_model=DonationResponse,
    summary="[FINANCIAL/ADMIN] Get a donation by ID",
)
@route_logger
def get_donation(
    request: Request,
    donation_id: int,
    service: DonationService = Depends(DonationService),
):
    return service.get_by_id(donation_id)


@donations_router.post(
    "",
    response_model=DonationResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register a donation (money or items)",
)
@route_logger
def create_donation(
    request: Request,
    body: DonationCreateRequest,
    service: DonationService = Depends(DonationService),
):
    return service.create(body)


@donations_router.patch(
    "/{donation_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate a donation",
)
@route_logger
def deactivate_donation(
    request: Request,
    donation_id: int,
    service: DonationService = Depends(DonationService),
):
    return service.deactivate(donation_id)
