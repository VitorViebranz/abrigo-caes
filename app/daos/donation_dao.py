from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import DonationModel, DonationItemModel


class DonationDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, include_inactive: bool = False) -> list[DonationModel]:
        stmt = (
            select(DonationModel)
            .options(selectinload(DonationModel.items))
            .order_by(DonationModel.date.desc())
        )
        if not include_inactive:
            stmt = stmt.where(DonationModel.is_active == True)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, donation_id: int) -> DonationModel | None:
        stmt = (
            select(DonationModel)
            .options(selectinload(DonationModel.items))
            .where(DonationModel.id == donation_id)
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, donation: DonationModel, items: list[DonationItemModel]) -> DonationModel:
        self._session.add(donation)
        await self._session.flush()
        for item in items:
            item.donation_id = donation.id
            self._session.add(item)
        await self._session.flush()
        await self._session.refresh(donation)
        return donation

    async def deactivate(self, donation_id: int) -> bool:
        result = await self._session.execute(
            update(DonationModel)
            .where(DonationModel.id == donation_id, DonationModel.is_active == True)
            .values(is_active=False)
        )
        return result.rowcount > 0
