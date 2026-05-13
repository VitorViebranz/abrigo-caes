from fastapi import HTTPException, status

from daos import UserDAO, RoleDAO, PermissionDAO
from configs.pagination import MAX_PAGE_SIZE
from schemas import UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse, PaginationInfo
from utils import hash_password


class UserService:

    def __init__(self):
        self._dao = UserDAO()
        self._role_dao = RoleDAO()
        self._permission_dao = PermissionDAO()

    def get_all(self, page: int, page_size: int) -> UserListResponse:
        effective_page_size = min(page_size, MAX_PAGE_SIZE)
        users, total = self._dao.get_page(page=page, page_size=effective_page_size)
        return UserListResponse(
            data=[UserResponse.model_validate(u) for u in users],
            pagination=PaginationInfo(
                actual_page=page,
                page_size=effective_page_size,
                total_records=total,
                total_pages=(total + effective_page_size - 1) // effective_page_size,
            ),
        )

    def get_by_id(self, user_id: int) -> UserResponse:
        user = self._dao.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserResponse.model_validate(user)

    def create(self, request: UserCreateRequest) -> UserResponse:
        existing = self._dao.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{request.email}' is already registered.",
            )

        role_id = self._resolve_role_id(request.role, request.permissions)
        user = self._dao.create(
            full_name=request.full_name,
            email=request.email,
            hashed_password=hash_password(request.password),
            role_id=role_id,
        )
        return UserResponse.model_validate(user)

    def update(self, user_id: int, request: UserUpdateRequest) -> UserResponse:
        updates = request.model_dump(exclude_none=True)
        role_name = updates.pop("role", None)
        permissions = updates.pop("permissions", None)
        if not updates and role_name is None and permissions is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )

        if role_name is not None or permissions is not None:
            role_id = self._resolve_role_id(role_name or "voluntario", permissions)
            updates["role_id"] = role_id

        user = self._dao.update(user_id, **updates)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserResponse.model_validate(user)

    def _resolve_role_id(self, role_name: str, permissions: list[str] | None) -> int | None:
        role = self._role_dao.get_by_name(role_name)
        if not role:
            role = self._role_dao.create(role_name)

        if permissions is not None:
            permission_ids = []
            for name in permissions:
                permission = self._permission_dao.get_by_name(name)
                if not permission:
                    permission = self._permission_dao.create(name, None)
                permission_ids.append(permission.id)
            self._role_dao.set_permissions(role.id, permission_ids)

        return role.id

    def deactivate(self, user_id: int) -> dict:
        user = self._dao.update_active(user_id, is_active=False)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return {"message": f"User '{user.email}' deactivated successfully."}

    def activate(self, user_id: int) -> dict:
        user = self._dao.update_active(user_id, is_active=True)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return {"message": f"User '{user.email}' activated successfully."}
