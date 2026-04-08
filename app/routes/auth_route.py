from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas import LoginRequest, TokenResponse
from services import AuthService
from configs import route_logger

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@route_logger()
@auth_router.post("/login", response_model=TokenResponse, summary="Login (Integrado com Swagger)")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(AuthService)
):
    request = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    return service.login(request)