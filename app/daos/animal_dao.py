from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import selectinload
from configs import PostgresConnection

from .vaccine_dao import VaccineDAO
from schemas import AnimalCreateRequest, AnimalUpdateRequest
from models import AnimalModel, AdoptionStatus


class AnimalDAO:

    def __init__(self):
        self._vaccine_dao = VaccineDAO()

    def get_page(self, include_inactive: bool, page: int, page_size: int) -> tuple[list[AnimalModel], int]:
        with PostgresConnection() as session:
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

            total = session.execute(count_stmt).scalar_one()
            items = session.execute(data_stmt).scalars().all()
            return items, total

    def get_by_id(self, animal_id: int) -> AnimalModel | None:
        with PostgresConnection() as session:
            stmt = select(AnimalModel).where(AnimalModel.id == animal_id).options(selectinload(AnimalModel.vaccines))
            return session.execute(stmt).scalar_one_or_none()

    def get_by_status(self, status: AdoptionStatus) -> list[AnimalModel]:
        with PostgresConnection() as session:
            return session.execute(
                select(AnimalModel).where(AnimalModel.adoption_status == status, AnimalModel.is_active == True)
            ).scalars().all()

    def create(self, animal_create: AnimalCreateRequest) -> AnimalModel:
        with PostgresConnection() as session:
            animal_stmt = insert(AnimalModel).values(
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
            animal_result = session.execute(animal_stmt)
            animal_id = animal_result.inserted_primary_key[0]

            if animal_create.vaccines:
                self._vaccine_dao.create_bulk(animal_id, animal_create.vaccines, session)

        return self.get_by_id(animal_id)

    def update(self, animal_id: int, animal_update: AnimalUpdateRequest) -> AnimalModel | None:
        with PostgresConnection() as session:
            stmt_update = (
                update(AnimalModel)
                .where(AnimalModel.id == animal_id)
                .values(**animal_update.model_dump(exclude_unset=True))
            )
            session.execute(stmt_update)

    def update_image_path(self, animal_id: int, image_path: str | None) -> bool:
        with PostgresConnection() as session:
            result = session.execute(
                update(AnimalModel)
                .where(AnimalModel.id == animal_id)
                .values(image_path=image_path)
            )
            return result.rowcount > 0

    def deactivate(self, animal_id: int) -> bool:
        with PostgresConnection() as session:
            stmt = (
                update(AnimalModel)
                .where(AnimalModel.id == animal_id)
                .values(is_active=False)
            )
            result = session.execute(stmt)
            return result.rowcount > 0
        
    def update_status(self, animal_id: int, adoption_status: AdoptionStatus) -> AnimalModel | None:
        with PostgresConnection() as session:
            stmt = (
                update(AnimalModel)
                .where(AnimalModel.id == animal_id)
                .values(adoption_status=adoption_status)
            )
            session.execute(stmt)