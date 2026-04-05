from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas import LoginRequest, TokenResponse
from services import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=TokenResponse, summary="Login")
def login(request: LoginRequest, service: AuthService = Depends(AuthService)):
    return service.login(request)


@auth_router.post("/token", response_model=TokenResponse, summary="OAuth2 token (Swagger UI)")
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(AuthService),
):
    """Endpoint used by Swagger UI's Authorize button."""
    return service.login(LoginRequest(email=form_data.username, password=form_data.password))
