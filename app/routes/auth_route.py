from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from schemas import LoginRequest, TokenResponse
from services import AuthService
from configs import route_logger

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=TokenResponse, summary="Login (Integrado com Swagger)")
@route_logger
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    login_request = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    return await service.login(login_request)