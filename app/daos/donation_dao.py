from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from configs import PostgresConnection
from models import DonationModel, DonationItemModel


class DonationDAO:

    def get_all(self, include_inactive: bool = False) -> list[DonationModel]:
        with PostgresConnection() as session:
            stmt = (
                select(DonationModel)
                .options(selectinload(DonationModel.items))
                .order_by(DonationModel.date.desc())
            )
            if not include_inactive:
                stmt = stmt.where(DonationModel.is_active == True)
            return session.execute(stmt).scalars().all()

    def get_by_id(self, donation_id: int) -> DonationModel | None:
        with PostgresConnection() as session:
            stmt = (
                select(DonationModel)
                .options(selectinload(DonationModel.items))
                .where(DonationModel.id == donation_id)
            )
            return session.execute(stmt).scalar_one_or_none()

    def create(self, donation: DonationModel, items: list[DonationItemModel]) -> DonationModel:
        with PostgresConnection() as session:
            session.add(donation)
            session.flush()
            for item in items:
                item.donation_id = donation.id
                session.add(item)
            session.flush()
            session.refresh(donation)
            return donation

    def deactivate(self, donation_id: int) -> bool:
        with PostgresConnection() as session:
            result = session.execute(
                update(DonationModel)
                .where(DonationModel.id == donation_id, DonationModel.is_active == True)
                .values(is_active=False)
            )
            return result.rowcount > 0
