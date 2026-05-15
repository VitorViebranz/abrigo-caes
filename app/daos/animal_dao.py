from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .vaccine_dao import VaccineDAO
from schemas import AnimalCreateRequest, AnimalUpdateRequest
from models import AnimalModel, AdoptionStatus


class AnimalDAO:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._vaccine_dao = VaccineDAO(session)

    async def get_page(self, include_inactive: bool, page: int, page_size: int) -> tuple[list[AnimalModel], int]:
        offset = (page - 1) * page_size
        filters = []
        if not include_inactive:
            filters.append(AnimalModel.is_active == True)

        count_stmt = select(func.count()).select_from(AnimalModel)
        if filters:
            count_stmt = count_stmt.where(*filters)

        data_stmt = (
            select(AnimalModel)
            .options(selectinload(AnimalModel.vaccines))
            .order_by(AnimalModel.id)
            .offset(offset)
            .limit(page_size)
        )
        if filters:
            data_stmt = data_stmt.where(*filters)

        total_result = await self._session.execute(count_stmt)
        data_result = await self._session.execute(data_stmt)
        total = total_result.scalar_one()
        items = data_result.scalars().all()
        return items, total

    async def get_by_id(self, animal_id: int) -> AnimalModel | None:
        stmt = (
            select(AnimalModel)
            .where(AnimalModel.id == animal_id)
            .options(selectinload(AnimalModel.vaccines))
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_status(self, status: AdoptionStatus) -> list[AnimalModel]:
        result = await self._session.execute(
            select(AnimalModel).where(AnimalModel.adoption_status == status, AnimalModel.is_active == True)
        )
        return result.scalars().all()

    async def create(self, animal_create: AnimalCreateRequest) -> AnimalModel:
        animal_stmt = (
            insert(AnimalModel)
            .values(
                name=animal_create.name,
                estimated_age=animal_create.estimated_age,
                size=animal_create.size,
                species=animal_create.species,
                entry_date=animal_create.entry_date,
                notes=animal_create.notes,
                neutered=animal_create.neutered,
                dewormed=animal_create.dewormed,
                socializes_with_other_animals=animal_create.socializes_with_other_animals,
                color=animal_create.color,
                microchipped=animal_create.microchipped,
            )
            .returning(AnimalModel.id)
        )
        result = await self._session.execute(animal_stmt)
        animal_id = result.scalar_one()

        if animal_create.vaccines:
            await self._vaccine_dao.create_bulk(animal_id, animal_create.vaccines)

        return await self.get_by_id(animal_id)

    async def update(self, animal_id: int, animal_update: AnimalUpdateRequest) -> None:
        stmt_update = (
            update(AnimalModel)
            .where(AnimalModel.id == animal_id)
            .values(**animal_update.model_dump(exclude_unset=True))
        )
        await self._session.execute(stmt_update)

    async def update_image_path(self, animal_id: int, image_path: str | None) -> bool:
        result = await self._session.execute(
            update(AnimalModel)
            .where(AnimalModel.id == animal_id)
            .values(image_path=image_path)
        )
        return result.rowcount > 0

    async def deactivate(self, animal_id: int) -> bool:
        stmt = (
            update(AnimalModel)
            .where(AnimalModel.id == animal_id)
            .values(is_active=False)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
        
    async def update_status(self, animal_id: int, adoption_status: AdoptionStatus) -> None:
        stmt = (
            update(AnimalModel)
            .where(AnimalModel.id == animal_id)
            .values(adoption_status=adoption_status)
        )
        await self._session.execute(stmt)