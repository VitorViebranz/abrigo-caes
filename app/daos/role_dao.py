from sqlalchemy import delete, insert, select
from configs import PostgresConnection
from models import RoleModel, PermissionModel, role_permissions


class RoleDAO:
    def get_all(self) -> list[RoleModel]:
        with PostgresConnection() as session:
            stmt = select(RoleModel).order_by(RoleModel.name.asc())
            return session.execute(stmt).unique().scalars().all()

    def get_by_name(self, name: str) -> RoleModel | None:
        with PostgresConnection() as session:
            stmt = select(RoleModel).where(RoleModel.name == name)
            return session.execute(stmt).unique().scalar_one_or_none()

    def get_by_id(self, role_id: int) -> RoleModel | None:
        with PostgresConnection() as session:
            stmt = select(RoleModel).where(RoleModel.id == role_id)
            return session.execute(stmt).unique().scalar_one_or_none()

    def create(self, name: str) -> RoleModel:
        with PostgresConnection() as session:
            stmt = insert(RoleModel).values(name=name)
            session.execute(stmt)
            session.commit()
            return self.get_by_name(name)

    def set_permissions(self, role_id: int, permission_ids: list[int]) -> None:
        with PostgresConnection() as session:
            session.execute(
                delete(role_permissions).where(role_permissions.c.role_id == role_id)
            )
            if permission_ids:
                session.execute(
                    insert(role_permissions).values(
                        [
                            {"role_id": role_id, "permission_id": pid}
                            for pid in permission_ids
                        ]
                    )
                )
            session.commit()

    def get_permissions_by_role(self, role_id: int) -> list[PermissionModel]:
        with PostgresConnection() as session:
            stmt = (
                select(PermissionModel)
                .join(role_permissions, PermissionModel.id == role_permissions.c.permission_id)
                .where(role_permissions.c.role_id == role_id)
                .order_by(PermissionModel.name.asc())
            )
            return session.execute(stmt).scalars().all()
