from sqlalchemy import insert, select
from configs import PostgresConnection
from models import PermissionModel


class PermissionDAO:
    def get_all(self) -> list[PermissionModel]:
        with PostgresConnection() as session:
            stmt = select(PermissionModel).order_by(PermissionModel.name.asc())
            return session.execute(stmt).scalars().all()

    def get_by_name(self, name: str) -> PermissionModel | None:
        with PostgresConnection() as session:
            stmt = select(PermissionModel).where(PermissionModel.name == name)
            return session.execute(stmt).scalar_one_or_none()

    def create(self, name: str, description: str | None = None) -> PermissionModel:
        with PostgresConnection() as session:
            stmt = insert(PermissionModel).values(name=name, description=description)
            session.execute(stmt)
            session.commit()
            return self.get_by_name(name)
