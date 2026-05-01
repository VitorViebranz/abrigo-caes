from fastapi import Depends, HTTPException, status
from configs.security import verify_token
from configs import MySQLConnection
from models import PermissionModel, RoleModel
from sqlalchemy import select


def get_user_permissions(current_user = Depends(verify_token)) -> list[str]:
    if not current_user or not getattr(current_user, "role_id", None):
        return []

    with MySQLConnection() as session:
        stmt = select(RoleModel).where(RoleModel.id == current_user.role_id)
        role = session.execute(stmt).unique().scalar_one_or_none()
        if not role:
            return []
        return [p.name for p in role.permissions]


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user = Depends(verify_token)):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        if not getattr(current_user, "role_id", None):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        with MySQLConnection() as session:
            stmt = select(RoleModel).where(RoleModel.id == current_user.role_id)
            role = session.execute(stmt).unique().scalar_one_or_none()
            
            if not role:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not found.")

            user_permissions = [p.name for p in role.permissions]

            if "manage_all" not in user_permissions and self.required_permission not in user_permissions:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return current_user
