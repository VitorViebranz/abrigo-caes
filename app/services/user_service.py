from fastapi import HTTPException, status

from daos import UserDAO
from schemas import UserCreateRequest, UserUpdateRequest, UserResponse
from utils import hash_password


class UserService:

    def __init__(self):
        self._dao = UserDAO()

    def get_all(self) -> list[UserResponse]:
        users = self._dao.get_all()
        return [UserResponse.model_validate(u) for u in users]

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


        user = self._dao.create(
            full_name=request.full_name,
            email=request.email,
            hashed_password=hash_password(request.password),
            role=request.role,
        )
        return UserResponse.model_validate(user)

    def update(self, user_id: int, request: UserUpdateRequest) -> UserResponse:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )


        user = self._dao.update(user_id, **updates)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
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
