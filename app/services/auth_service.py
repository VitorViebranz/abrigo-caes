from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from configs.security import EXPIRE_MINUTES
from configs import create_access_token
from daos import UserDAO
from schemas import LoginRequest, TokenResponse
from utils import verify_password


class AuthService:
    def __init__(self, db: AsyncSession):
        self._dao = UserDAO(db)

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self._dao.get_by_email(request.email)

        invalid_credentials = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

        if not user:
            raise invalid_credentials

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account deactivated. Please contact the administrator.",
            )

        if not verify_password(request.password, user.hashed_password):
            raise invalid_credentials

        token = create_access_token({
            "sub": str(user.id)
        })

        expires_at = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
        await self._dao.update_token(user.id, token, expires_at)

        role_value = getattr(user.role, "name", None) or getattr(user.role, "value", None) or user.role
        return TokenResponse(
            access_token=token,
            user_name=user.full_name,
            user_email=user.email,
            role=role_value,
        )