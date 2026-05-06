from fastapi import HTTPException, status
from daos import PermissionDAO, RoleDAO
from schemas import RoleCreateRequest, RoleUpdateRequest, RoleResponse


class RoleService:
    def __init__(self):
        self._role_dao = RoleDAO()
        self._permission_dao = PermissionDAO()

    def get_all(self) -> list[RoleResponse]:
        roles = self._role_dao.get_all()
        responses = []
        for role in roles:
            permissions = [p.name for p in role.permissions]
            responses.append(RoleResponse(id=role.id, name=role.name, permissions=permissions))
        return responses

    def create(self, request: RoleCreateRequest) -> RoleResponse:
        existing = self._role_dao.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{request.name}' already exists.",
            )
        role = self._role_dao.create(request.name)
        self._apply_permissions(role.id, request.permissions)
        role = self._role_dao.get_by_id(role.id)
        permissions = [p.name for p in role.permissions] if role else []
        return RoleResponse(id=role.id, name=role.name, permissions=permissions)

    def update(self, role_id: int, request: RoleUpdateRequest) -> RoleResponse:
        role = self._role_dao.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")
        if request.permissions is not None:
            self._apply_permissions(role_id, request.permissions)
            role = self._role_dao.get_by_id(role_id)
        permissions = [p.name for p in role.permissions] if role else []
        return RoleResponse(id=role.id, name=role.name, permissions=permissions)

    def _apply_permissions(self, role_id: int, permission_names: list[str]) -> None:
        if not permission_names:
            self._role_dao.set_permissions(role_id, [])
            return
        permission_ids = []
        for name in permission_names:
            permission = self._permission_dao.get_by_name(name)
            if not permission:
                permission = self._permission_dao.create(name, None)
            permission_ids.append(permission.id)
        self._role_dao.set_permissions(role_id, permission_ids)
