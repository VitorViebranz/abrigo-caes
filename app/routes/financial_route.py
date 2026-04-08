from fastapi import APIRouter, Depends

from configs.security import verify_token
from configs import require_financial_or_admin
from schemas import FinancialCreateRequest, FinancialResponse, MonthlyReportResponse
from services import FinancialService

financial_router = APIRouter(prefix="/financial", tags=["Financial"])


@financial_router.get(
    "",
    response_model=list[FinancialResponse],
    summary="[FINANCIAL/ADMIN] List all active financial records"
)
def get_all(
    service: FinancialService = Depends(FinancialService),
    current_user: dict = Depends(verify_token)
):
    return service.get_all()


@financial_router.post(
    "",
    response_model=FinancialResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register an income or expense"
)
def create_record(
    request: FinancialCreateRequest,
    service: FinancialService = Depends(FinancialService),
    current_user: dict = Depends(verify_token)
):
    return service.create(request)


@financial_router.patch(
    "/{record_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate a record (records cannot be deleted)"
)
def deactivate_record(
    record_id: int,
    service: FinancialService = Depends(FinancialService),
    current_user: dict = Depends(verify_token)
):
    return service.deactivate(record_id)


@financial_router.get(
    "/report/{year}/{month}",
    response_model=MonthlyReportResponse,
    summary="[FINANCIAL/ADMIN] Monthly report with income, expenses and balance"
)
def monthly_report(
    year: int,
    month: int,
    service: FinancialService = Depends(FinancialService),
    current_user: dict = Depends(verify_token)
):
    return service.get_monthly_report(year, month)
