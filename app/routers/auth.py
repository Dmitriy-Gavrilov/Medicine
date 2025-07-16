from authx import AuthX, AuthXConfig
from authx.exceptions import MissingTokenError, JWTDecodeError
from fastapi import APIRouter, Response, Request, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.exceptions.auth import AuthError, TokenExpiredError
from app.schemas.auth import AuthSchema, AuthResponseSchema
from app.services.auth_service import AuthService
from app.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

config = AuthXConfig(
    JWT_ALGORITHM='HS256',
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME=settings.JWT_COOKIE_NAME,
    JWT_REFRESH_COOKIE_NAME=settings.JWT_REFRESH_COOKIE_NAME,
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES=settings.JWT_REFRESH_TOKEN_EXPIRES
)

security = AuthX(config=config)

service = AuthService()


@router.post(path="/login",
             summary="Войти в систему",
             response_model=AuthResponseSchema,
             dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def login(auth: AuthSchema,
                response: Response,
                session: AsyncSession = Depends(get_session)):
    user = await service.check_user(auth, session)

    access_token = security.create_access_token(uid=str(user.id), data={"role": user.role})
    refresh_token = security.create_refresh_token(uid=str(user.id))

    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token, httponly=True, samesite="none", secure=True)
    response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, refresh_token, httponly=True, samesite="none", secure=True)
    return AuthResponseSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(path="/logout",
             summary="Выйти из системы")
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)


@router.post(path="/refresh",
             summary="Обновить access токен",
             dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def refresh(request: Request,
                  response: Response,
                  session: AsyncSession = Depends(get_session)):
    try:
        refresh_token = await security.get_refresh_token_from_request(request)
        token_payload = security.verify_token(refresh_token, verify_csrf=False)
        user_id = int(token_payload.sub)

        user = await service.get_user(user_id, session)
        new_access_token = security.create_access_token(uid=str(user_id), data={"role": user.role})

        response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, new_access_token, httponly=True, samesite="none",
                            secure=True)
    except MissingTokenError:
        raise AuthError()
    except JWTDecodeError:
        raise TokenExpiredError()
