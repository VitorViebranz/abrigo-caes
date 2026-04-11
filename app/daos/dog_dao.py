from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload
from configs import MySQLConnection

from .vaccine_dao import VaccineDAO
from schemas import DogCreateRequest, DogUpdateRequest
from models import DogModel, AdoptionStatus


class DogDAO:

    def __init__(self):
        self._vaccine_dao = VaccineDAO()

    def get_all(self, include_inactive: bool = False) -> list[DogModel]:
        with MySQLConnection() as session:
            stmt = select(DogModel).options(selectinload(DogModel.vaccines))
            if not include_inactive:
                stmt = stmt.where(DogModel.is_active == True)
            return session.execute(stmt).scalars().all()

    def get_by_id(self, dog_id: int) -> DogModel | None:
        with MySQLConnection() as session:
            stmt = select(DogModel).where(DogModel.id == dog_id).options(selectinload(DogModel.vaccines))
            return session.execute(stmt).scalar_one_or_none()

    def get_by_status(self, status: AdoptionStatus) -> list[DogModel]:
        with MySQLConnection() as session:
            return session.execute(
                select(DogModel).where(DogModel.adoption_status == status, DogModel.is_active == True)
            ).scalars().all()

    def create(self, dog_create: DogCreateRequest) -> DogModel:
        with MySQLConnection() as session:
            dog_stmt = insert(DogModel).values(
                name=dog_create.name,
                estimated_age=dog_create.estimated_age,
                size=dog_create.size,
                entry_date=dog_create.entry_date,
                notes=dog_create.notes,
                neutered=dog_create.neutered,
                dewormed=dog_create.dewormed,
                socializes_with_other_dogs=dog_create.socializes_with_other_dogs,
                color=dog_create.color,
            )
            dog_result = session.execute(dog_stmt)
            dog_id = dog_result.inserted_primary_key[0]

            if dog_create.vaccines:
                self._vaccine_dao.create_bulk(dog_id, dog_create.vaccines, session)

    def update(self, dog_id: int, dog_update: DogUpdateRequest) -> DogModel | None:
        with MySQLConnection() as session:
            stmt_update = (
                update(DogModel)
                .where(DogModel.id == dog_id)
                .values(**dog_update.model_dump(exclude_unset=True))
            )
            session.execute(stmt_update)

    def deactivate(self, dog_id: int) -> bool:
        with MySQLConnection() as session:
            stmt = (
                update(DogModel)
                .where(DogModel.id == dog_id)
                .values(is_active=False)
            )
            result = session.execute(stmt)
            return result.rowcount > 0
        
    def update_status(self, dog_id: int, adoption_status: AdoptionStatus) -> DogModel | None:
        with MySQLConnection() as session:
            stmt = (
                update(DogModel)
                .where(DogModel.id == dog_id)
                .values(adoption_status=adoption_status)
            )
            session.execute(stmt)