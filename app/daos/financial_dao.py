from datetime import date
from sqlalchemy import select, extract
from models import FinancialModel, FinancialType
from configs import MySQLConnection


class FinancialDAO:

    def __init__(self):
        pass

    def get_all(self, include_inactive: bool = False) -> list[FinancialModel]:
        with MySQLConnection() as session:
            stmt = select(FinancialModel)
            if not include_inactive:
                stmt = stmt.where(FinancialModel.is_active == True)
            return session.execute(stmt.order_by(FinancialModel.date.desc())).scalars().all()

    def get_by_id(self, record_id: int) -> FinancialModel | None:
        with MySQLConnection() as session:
            return session.execute(
                select(FinancialModel).where(FinancialModel.id == record_id)
            ).scalar_one_or_none()

    def get_by_month(self, year: int, month: int) -> list[FinancialModel]:
        with MySQLConnection() as session:
            return session.execute(
                select(FinancialModel).where(
                    FinancialModel.is_active == True,
                    extract("year", FinancialModel.date) == year,
                    extract("month", FinancialModel.date) == month,
                ).order_by(FinancialModel.date.desc())
            ).scalars().all()

    def create(self, **kwargs) -> FinancialModel:
        record = FinancialModel(**kwargs)
        with MySQLConnection() as session:
            session.add(record)
            session.flush()
            session.refresh(record)
            return record

    def deactivate(self, record_id: int) -> bool:
        with MySQLConnection() as session:
            record = session.execute(
                select(FinancialModel).where(FinancialModel.id == record_id)
            ).scalar_one_or_none()
            if not record:
                return False
            record.is_active = False
            return True
