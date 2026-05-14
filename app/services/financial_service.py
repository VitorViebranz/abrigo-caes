from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from daos import FinancialDAO
from models import FinancialType
from schemas import FinancialCreateRequest, FinancialResponse, MonthlyReportResponse


class FinancialService:
    def __init__(self, db: AsyncSession):
        self._dao = FinancialDAO(db)

    async def get_all(self) -> list[FinancialResponse]:
        records = await self._dao.get_all()
        return [FinancialResponse.model_validate(r) for r in records]

    async def get_by_id(self, record_id: int) -> FinancialResponse:
        record = await self._dao.get_by_id(record_id)
        if not record or not record.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial record not found.",
            )
        return FinancialResponse.model_validate(record)

    async def create(self, request: FinancialCreateRequest) -> FinancialResponse:
        record = await self._dao.create(**request.model_dump())
        return FinancialResponse.model_validate(record)

    async def deactivate(self, record_id: int) -> dict:
        success = await self._dao.deactivate(record_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial record not found.",
            )
        return {"message": "Record deactivated. Financial records are never permanently deleted."}

    async def get_monthly_report(self, year: int, month: int) -> MonthlyReportResponse:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Month must be between 1 and 12.",
            )

        records = await self._dao.get_by_month(year, month)

        total_income   = sum(float(r.value) for r in records if r.type == FinancialType.entrada)
        total_expenses = sum(float(r.value) for r in records if r.type == FinancialType.saida)
        balance        = total_income - total_expenses

        return MonthlyReportResponse(
            year=year,
            month=month,
            total_income=round(total_income, 2),
            total_expenses=round(total_expenses, 2),
            balance=round(balance, 2),
            records=[FinancialResponse.model_validate(r) for r in records],
        )
