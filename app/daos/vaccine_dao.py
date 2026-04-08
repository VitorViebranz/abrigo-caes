from datetime import date, timedelta
from sqlalchemy import select
from models import VaccineModel
from configs import MySQLConnection


class VaccineDAO:

    def __init__(self):
        pass

    def get_by_dog(self, dog_id: int) -> list[VaccineModel]:
        with MySQLConnection() as session:
            return session.execute(
                select(VaccineModel).where(VaccineModel.dog_id == dog_id)
                .order_by(VaccineModel.application_date.desc())
            ).scalars().all()

    def get_by_id(self, vaccine_id: int) -> VaccineModel | None:
        with MySQLConnection() as session:
            return session.execute(
                select(VaccineModel).where(VaccineModel.id == vaccine_id)
            ).scalar_one_or_none()

    def get_overdue(self) -> list[VaccineModel]:
        """Vaccines where next_dose is in the past."""
        with MySQLConnection() as session:
            return session.execute(
                select(VaccineModel).where(VaccineModel.next_dose < date.today())
            ).scalars().all()

    def get_due_soon(self, days: int = 7) -> list[VaccineModel]:
        today     = date.today()
        threshold = today + timedelta(days=days)
        with MySQLConnection() as session:
            return session.execute(
                select(VaccineModel).where(
                    VaccineModel.next_dose >= today,
                    VaccineModel.next_dose <= threshold,
                )
            ).scalars().all()

    def create(self, **kwargs) -> VaccineModel:
        vaccine = VaccineModel(**kwargs)
        with MySQLConnection() as session:
            session.add(vaccine)
            session.flush()
            session.refresh(vaccine)
            return vaccine

    def update(self, vaccine_id: int, **kwargs) -> VaccineModel | None:
        with MySQLConnection() as session:
            vaccine = session.execute(
                select(VaccineModel).where(VaccineModel.id == vaccine_id)
            ).scalar_one_or_none()
            if not vaccine:
                return None
            for field, value in kwargs.items():
                setattr(vaccine, field, value)
            session.flush()
            session.refresh(vaccine)
            return vaccine
