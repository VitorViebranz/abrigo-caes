import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_conn import get_db

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "unsafe_default_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 480))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    from daos.user_dao import UserDAO
    
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_dao = UserDAO(db)
        user = await user_dao.get_by_token(token)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou sessão encerrada.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.token_expires_at and user.token_expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado no banco de dados.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    except JWTError:
        raise exc


def _require_role(*allowed_roles: str):
    async def dependency(current_user = Depends(verify_token)):
        role_name = getattr(current_user.role, "name", None) or getattr(current_user.role, "value", None) or current_user.role
        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Perfis necessários: {', '.join(allowed_roles)}.",
            )
        return current_user
    return dependency

require_admin = _require_role("admin")
require_volunteer_or_admin  = _require_role("admin", "voluntario")
require_financial_or_admin  = _require_role("admin", "financeiro")