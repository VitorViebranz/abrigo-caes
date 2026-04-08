from sqlalchemy import select
from models import DogModel, AdoptionStatus
from configs import MySQLConnection


class DogDAO:

    def __init__(self):
        pass

    def get_all(self, include_inactive: bool = False) -> list[DogModel]:
        with MySQLConnection() as session:
            stmt = select(DogModel)
            if not include_inactive:
                stmt = stmt.where(DogModel.is_active == True)
            return session.execute(stmt).scalars().all()

    def get_by_id(self, dog_id: int) -> DogModel | None:
        with MySQLConnection() as session:
            return session.execute(
                select(DogModel).where(DogModel.id == dog_id)
            ).scalar_one_or_none()

    def get_by_status(self, status: AdoptionStatus) -> list[DogModel]:
        with MySQLConnection() as session:
            return session.execute(
                select(DogModel).where(DogModel.adoption_status == status, DogModel.is_active == True)
            ).scalars().all()

    def create(self, **kwargs) -> DogModel:
        dog = DogModel(**kwargs)
        with MySQLConnection() as session:
            session.add(dog)
            session.flush()
            session.refresh(dog)
            return dog

    def update(self, dog_id: int, **kwargs) -> DogModel | None:
        with MySQLConnection() as session:
            dog = session.execute(
                select(DogModel).where(DogModel.id == dog_id)
            ).scalar_one_or_none()
            if not dog:
                return None
            for field, value in kwargs.items():
                setattr(dog, field, value)
            session.flush()
            session.refresh(dog)
            return dog

    def deactivate(self, dog_id: int) -> bool:
        with MySQLConnection() as session:
            dog = session.execute(
                select(DogModel).where(DogModel.id == dog_id)
            ).scalar_one_or_none()
            if not dog:
                return False
            dog.is_active = False
            return True
