from authx import AuthX, AuthXConfig
from fastapi import APIRouter, Response, Request

from app.schemas.auth import AuthSchema, AuthResponseSchema
from app.services.auth_service import AuthService
from app.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

config = AuthXConfig(
    JWT_ALGORITHM='HS256',
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME=settings.JWT_COOKIE_NAME,
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES
)

security = AuthX(config=config)

service = AuthService()


@router.post(path="/login",
             summary="Войти в систему",
             response_model=AuthResponseSchema)
async def login(auth: AuthSchema, response: Response):
    user = await service.check_user(auth)
    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="none", secure=True)
    return AuthResponseSchema(access_token=token)


@router.post(path="/logout",
             summary="Выйти из системы")
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)

