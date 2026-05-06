from datetime import date, timedelta
from sqlalchemy import insert, select, update
from models import VaccineModel
from configs import PostgresConnection


class VaccineDAO:

    def __init__(self):
        pass

    def get_by_animal(self, animal_id: int) -> list[VaccineModel]:
        with PostgresConnection() as session:
            return session.execute(
                select(VaccineModel)
                .where(VaccineModel.animal_id == animal_id, VaccineModel.is_active == True)
                .order_by(VaccineModel.application_date.desc())
            ).scalars().all()

    def get_by_id(self, vaccine_id: int) -> VaccineModel | None:
        with PostgresConnection() as session:
            return session.execute(
                select(VaccineModel).where(VaccineModel.id == vaccine_id)
            ).scalar_one_or_none()

    def get_overdue(self) -> list[VaccineModel]:
        """Vaccines where next_dose is in the past and the record is active."""
        with PostgresConnection() as session:
            return session.execute(
                select(VaccineModel).where(
                    VaccineModel.is_active == True,
                    VaccineModel.next_dose < date.today(),
                )
            ).scalars().all()

    def get_due_soon(self, days: int = 7) -> list[VaccineModel]:
        today     = date.today()
        threshold = today + timedelta(days=days)
        with PostgresConnection() as session:
            return session.execute(
                select(VaccineModel).where(
                    VaccineModel.is_active == True,
                    VaccineModel.next_dose >= today,
                    VaccineModel.next_dose <= threshold,
                )
            ).scalars().all()

    def create(self, **kwargs) -> VaccineModel:
        vaccine = VaccineModel(**kwargs)
        with PostgresConnection() as session:
            session.add(vaccine)
            session.flush()
            session.refresh(vaccine)
            return vaccine

    def update(self, vaccine_id: int, **kwargs) -> VaccineModel | None:
        with PostgresConnection() as session:
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

    def deactivate(self, vaccine_id: int) -> bool:
        with PostgresConnection() as session:
            result = session.execute(
                update(VaccineModel)
                .where(VaccineModel.id == vaccine_id, VaccineModel.is_active == True)
                .values(is_active=False)
            )
            return result.rowcount > 0

    def create_bulk(self, animal_id: int, vaccines: list[dict], session: any) -> None:
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
        session.execute(stmt_insert)