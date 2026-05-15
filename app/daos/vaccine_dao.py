from datetime import date, timedelta

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import VaccineModel


class VaccineDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_animal(self, animal_id: int) -> list[VaccineModel]:
        result = await self._session.execute(
            select(VaccineModel)
            .where(VaccineModel.animal_id == animal_id, VaccineModel.is_active == True)
            .order_by(VaccineModel.application_date.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, vaccine_id: int) -> VaccineModel | None:
        result = await self._session.execute(
            select(VaccineModel).where(VaccineModel.id == vaccine_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_overdue(self) -> list[VaccineModel]:
        """Vaccines where next_dose is in the past and the record is active."""
        result = await self._session.execute(
            select(VaccineModel).where(
                VaccineModel.is_active == True,
                VaccineModel.next_dose < date.today(),
            )
        )
        return result.scalars().all()

    async def get_due_soon(self, days: int = 7) -> list[VaccineModel]:
        today = date.today()
        threshold = today + timedelta(days=days)
        result = await self._session.execute(
            select(VaccineModel).where(
                VaccineModel.is_active == True,
                VaccineModel.next_dose >= today,
                VaccineModel.next_dose <= threshold,
            )
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> VaccineModel:
        vaccine = VaccineModel(**kwargs)
        self._session.add(vaccine)
        await self._session.flush()
        await self._session.refresh(vaccine)
        return vaccine

    async def update(self, vaccine_id: int, **kwargs) -> VaccineModel | None:
        result = await self._session.execute(
            select(VaccineModel).where(VaccineModel.id == vaccine_id)
        )
        vaccine = result.unique().scalar_one_or_none()
        if not vaccine:
            return None
        for field, value in kwargs.items():
            setattr(vaccine, field, value)
        await self._session.flush()
        await self._session.refresh(vaccine)
        return vaccine

    async def deactivate(self, vaccine_id: int) -> bool:
        result = await self._session.execute(
            update(VaccineModel)
            .where(VaccineModel.id == vaccine_id, VaccineModel.is_active == True)
            .values(is_active=False)
        )
        return result.rowcount > 0

    async def create_bulk(self, animal_id: int, vaccines: list[dict]) -> None:
        stmt_insert = insert(VaccineModel).values([
            {
                "animal_id": animal_id,
                "name": vaccine.name,
                "application_date": vaccine.application_date,
                "next_dose": vaccine.next_dose,
                "notes": vaccine.notes
            }
            for vaccine in vaccines
        ])
        await self._session.execute(stmt_insert)