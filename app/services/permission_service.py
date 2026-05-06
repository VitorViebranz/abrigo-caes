from fastapi import HTTPException, status
from daos import PermissionDAO
from schemas import PermissionCreateRequest, PermissionResponse


class PermissionService:
    def __init__(self):
        self._dao = PermissionDAO()

    def get_all(self) -> list[PermissionResponse]:
        permissions = self._dao.get_all()
        return [PermissionResponse.model_validate(p) for p in permissions]

    def create(self, request: PermissionCreateRequest) -> PermissionResponse:
        existing = self._dao.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission '{request.name}' already exists.",
            )
        permission = self._dao.create(request.name, request.description)
        return PermissionResponse.model_validate(permission)
