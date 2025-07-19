from authx.exceptions import MissingTokenError, JWTDecodeError
from authx.types import TokenLocation
from fastapi import Depends, Request, WebSocket
from authx import TokenPayload, RequestToken
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session, get_manual_session
from app.db.models import User
from app.db.models.user import UserRole
from app.db.repository import Repository
from app.exceptions.auth import AuthError, TokenExpiredError
from app.routers.auth import security
from app.utils.role_verifier import RoleVerifier


async def validate_token_from_request(request: Request) -> TokenPayload:
    try:
        token: RequestToken = await security.get_access_token_from_request(request)
        token.csrf = request.headers.get("X-CSRF-TOKEN")
        token_payload: TokenPayload = security.verify_token(token)
        return token_payload
    except MissingTokenError:
        raise AuthError()
    except JWTDecodeError:
        raise TokenExpiredError()


async def validate_token_from_request_ws(websocket: WebSocket) -> TokenPayload:
    try:
        token: RequestToken = RequestToken(token=websocket.cookies.get("access_token"), location="cookies")
        token.csrf = websocket.headers.get("X-CSRF-TOKEN")
        token_payload: TokenPayload = security.verify_token(token)
        return token_payload
    except MissingTokenError:
        raise AuthError()
    except JWTDecodeError:
        raise TokenExpiredError()


async def get_current_user(request: Request, session: AsyncSession) -> User:
    token_payload = await validate_token_from_request(request)

    user_id = int(token_payload.sub)
    user = await Repository(User).get_by_id(session, user_id)
    return user


async def get_current_user_ws(websocket: WebSocket, session: AsyncSession) -> User:
    token_payload = await validate_token_from_request_ws(websocket)

    user_id = int(token_payload.sub)
    user = await Repository(User).get_by_id(session, user_id)
    return user


def require_role(required_role: UserRole):
    async def dependency(
            request: Request,
            session: AsyncSession = Depends(get_session)
    ) -> User:
        current_user = await get_current_user(request, session)
        await RoleVerifier(current_user).verify(required_role)
        return current_user

    return dependency


def required_roles(required_roles: list[UserRole]):
    async def dependency(
            request: Request,
            session: AsyncSession = Depends(get_session)) -> User:
        current_user = await get_current_user(request, session)
        exception = None
        for role in required_roles:
            try:
                await RoleVerifier(current_user).verify(role)
                return current_user
            except Exception as e:
                exception = e
        raise exception

    return dependency


def require_role_ws(required_role: UserRole):
    async def dependency(websocket: WebSocket) -> User:
        async with get_manual_session() as session:
            current_user = await get_current_user_ws(websocket, session)
            await RoleVerifier(current_user).verify(required_role)
            return current_user

    return dependency
