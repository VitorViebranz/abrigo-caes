from sqlalchemy import Column, Integer, String, Table, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base_model import BaseModel


# Association table between roles and permissions
role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class PermissionModel(BaseModel):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)


class RoleModel(BaseModel):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    permissions = relationship(
        "PermissionModel",
        secondary=role_permissions,
        backref="roles",
        lazy="joined",
    )
