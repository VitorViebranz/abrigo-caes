from sqlalchemy import select
from models import Dog, AdoptionStatus
from configs import MySQLConnection


class DogDAO:

    def __init__(self):
        pass

    def get_all(self, include_inactive: bool = False) -> list[Dog]:
        with MySQLConnection() as session:
            stmt = select(Dog)
            if not include_inactive:
                stmt = stmt.where(Dog.is_active == True)
            return session.execute(stmt).scalars().all()

    def get_by_id(self, dog_id: int) -> Dog | None:
        with MySQLConnection() as session:
            return session.execute(
                select(Dog).where(Dog.id == dog_id)
            ).scalar_one_or_none()

    def get_by_status(self, status: AdoptionStatus) -> list[Dog]:
        with MySQLConnection() as session:
            return session.execute(
                select(Dog).where(Dog.adoption_status == status, Dog.is_active == True)
            ).scalars().all()

    def create(self, **kwargs) -> Dog:
        dog = Dog(**kwargs)
        with MySQLConnection() as session:
            session.add(dog)
            session.flush()
            session.refresh(dog)
            return dog

    def update(self, dog_id: int, **kwargs) -> Dog | None:
        with MySQLConnection() as session:
            dog = session.execute(
                select(Dog).where(Dog.id == dog_id)
            ).scalar_one_or_none()
            if not dog:
                return None
            for field, value in kwargs.items():
                setattr(dog, field, value)
            session.flush()
            session.refresh(dog)
            return dog

    def deactivate(self, dog_id: int) -> bool:
        """Soft delete — only admins should call this via service."""
        with MySQLConnection() as session:
            dog = session.execute(
                select(Dog).where(Dog.id == dog_id)
            ).scalar_one_or_none()
            if not dog:
                return False
            dog.is_active = False
            return True
