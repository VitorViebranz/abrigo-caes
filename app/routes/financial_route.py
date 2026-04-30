from fastapi import APIRouter, Depends, Request

from configs.security import verify_token
from configs import require_financial_or_admin
from configs.decorators import route_logger
from schemas import FinancialCreateRequest, FinancialResponse, MonthlyReportResponse
from services import FinancialService

financial_router = APIRouter(
    prefix="/financial",
    tags=["Financial"],
    dependencies=[Depends(require_financial_or_admin)],
)


@financial_router.get(
    "",
    response_model=list[FinancialResponse],
    summary="[FINANCIAL/ADMIN] List all active financial records"
)
@route_logger
def get_all(request: Request, service: FinancialService = Depends(FinancialService)):
    return service.get_all()


@financial_router.get(
    "/report/{year}/{month}",
    response_model=MonthlyReportResponse,
    summary="[FINANCIAL/ADMIN] Monthly report with income, expenses and balance"
)
@route_logger
def monthly_report(
    request: Request,
    year: int,
    month: int,
    service: FinancialService = Depends(FinancialService),
):
    return service.get_monthly_report(year, month)


@financial_router.get(
    "/{record_id}",
    response_model=FinancialResponse,
    summary="[FINANCIAL/ADMIN] Get a financial record by ID"
)
@route_logger
def get_record(
    request: Request,
    record_id: int,
    service: FinancialService = Depends(FinancialService),
):
    return service.get_by_id(record_id)


@financial_router.post(
    "",
    response_model=FinancialResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register an income or expense"
)
@route_logger
def create_record(
    request: Request,
    body: FinancialCreateRequest,
    service: FinancialService = Depends(FinancialService),
):
    return service.create(body)


@financial_router.patch(
    "/{record_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate a record (records cannot be deleted)"
)
@route_logger
def deactivate_record(
    request: Request,
    record_id: int,
    service: FinancialService = Depends(FinancialService),
):
    return service.deactivate(record_id)
