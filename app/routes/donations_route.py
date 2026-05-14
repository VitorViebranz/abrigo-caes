from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
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
async def list_donations(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = DonationService(db)
    return await service.get_all()


@donations_router.get(
    "/{donation_id}",
    response_model=DonationResponse,
    summary="[FINANCIAL/ADMIN] Get a donation by ID",
)
@route_logger
async def get_donation(
    request: Request,
    donation_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = DonationService(db)
    return await service.get_by_id(donation_id)


@donations_router.post(
    "",
    response_model=DonationResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register a donation (money or items)",
)
@route_logger
async def create_donation(
    request: Request,
    body: DonationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DonationService(db)
    return await service.create(body)


@donations_router.patch(
    "/{donation_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate a donation",
)
@route_logger
async def deactivate_donation(
    request: Request,
    donation_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = DonationService(db)
    return await service.deactivate(donation_id)
