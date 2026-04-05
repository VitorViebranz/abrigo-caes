from datetime import date
from sqlalchemy import select, extract
from models import Financial, FinancialType
from configs import MySQLConnection


class FinancialDAO:

    def __init__(self):
        pass

    def get_all(self, include_inactive: bool = False) -> list[Financial]:
        with MySQLConnection() as session:
            stmt = select(Financial)
            if not include_inactive:
                stmt = stmt.where(Financial.is_active == True)
            return session.execute(stmt.order_by(Financial.date.desc())).scalars().all()

    def get_by_id(self, record_id: int) -> Financial | None:
        with MySQLConnection() as session:
            return session.execute(
                select(Financial).where(Financial.id == record_id)
            ).scalar_one_or_none()

    def get_by_month(self, year: int, month: int) -> list[Financial]:
        with MySQLConnection() as session:
            return session.execute(
                select(Financial).where(
                    Financial.is_active == True,
                    extract("year", Financial.date) == year,
                    extract("month", Financial.date) == month,
                ).order_by(Financial.date.desc())
            ).scalars().all()

    def create(self, **kwargs) -> Financial:
        record = Financial(**kwargs)
        with MySQLConnection() as session:
            session.add(record)
            session.flush()
            session.refresh(record)
            return record

    def deactivate(self, record_id: int) -> bool:
        """
        Business rule: financial records cannot be deleted.
        Only deactivation is allowed.
        """
        with MySQLConnection() as session:
            record = session.execute(
                select(Financial).where(Financial.id == record_id)
            ).scalar_one_or_none()
            if not record:
                return False
            record.is_active = False
            return True
