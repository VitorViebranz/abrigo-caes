from fastapi import HTTPException, status

from daos import UserDAO
from schemas import UserCreateRequest, UserResponse
from utils import hash_password


class UserService:

    def __init__(self):
        self._dao = UserDAO()

    def get_all(self) -> list[UserResponse]:
        users = self._dao.get_all()
        return [UserResponse(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        ) for u in users]

    def create(self, request: UserCreateRequest) -> UserResponse:
        existing = self._dao.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{request.email}' is already registered.",
            )

        valid_roles = {"admin", "voluntario", "financeiro"}
        if request.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}.",
            )

        user = self._dao.create(
            full_name=request.full_name,
            email=request.email,
            hashed_password=hash_password(request.password),
            role=request.role,
        )
        return UserResponse.model_validate(user)

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
