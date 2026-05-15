from datetime import date

from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import FinancialModel, FinancialType


class FinancialDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, include_inactive: bool = False) -> list[FinancialModel]:
        stmt = select(FinancialModel)
        if not include_inactive:
            stmt = stmt.where(FinancialModel.is_active == True)
        result = await self._session.execute(stmt.order_by(FinancialModel.date.desc()))
        return result.scalars().all()

    async def get_by_id(self, record_id: int) -> FinancialModel | None:
        result = await self._session.execute(
            select(FinancialModel).where(FinancialModel.id == record_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_month(self, year: int, month: int) -> list[FinancialModel]:
        result = await self._session.execute(
            select(FinancialModel).where(
                FinancialModel.is_active == True,
                extract("year", FinancialModel.date) == year,
                extract("month", FinancialModel.date) == month,
            ).order_by(FinancialModel.date.desc())
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> FinancialModel:
        record = FinancialModel(**kwargs)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def deactivate(self, record_id: int) -> bool:
        result = await self._session.execute(
            select(FinancialModel).where(FinancialModel.id == record_id)
        )
        record = result.unique().scalar_one_or_none()
        if not record:
            return False
        record.is_active = False
        return True
