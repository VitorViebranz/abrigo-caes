from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import FinancialCreateRequest, FinancialResponse, MonthlyReportResponse
from services import FinancialService

financial_router = APIRouter(
    prefix="/financial",
    tags=["Financial"],
    dependencies=[Depends(PermissionChecker("manage_finances"))],
)

@financial_router.get(
    "",
    response_model=list[FinancialResponse],
    summary="[FINANCIAL/ADMIN] List all active financial records"
)
@route_logger
async def get_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.get_all()

@financial_router.get(
    "/report/{year}/{month}",
    response_model=MonthlyReportResponse,
    summary="[FINANCIAL/ADMIN] Monthly report with income, expenses and balance"
)
@route_logger
async def monthly_report(
    request: Request,
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.get_monthly_report(year, month)

@financial_router.get(
    "/{record_id}",
    response_model=FinancialResponse,
    summary="[FINANCIAL/ADMIN] Get a financial record by ID"
)
@route_logger
async def get_record(
    request: Request,
    record_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.get_by_id(record_id)

@financial_router.post(
    "",
    response_model=FinancialResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register an income or expense"
)
@route_logger
async def create_record(
    request: Request,
    body: FinancialCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.create(body)

@financial_router.patch(
    "/{record_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate a record (records cannot be deleted)"
)
@route_logger
async def deactivate_record(
    request: Request,
    record_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.deactivate(record_id)