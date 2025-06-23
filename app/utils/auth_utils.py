from authx.exceptions import MissingTokenError, JWTDecodeError
from fastapi import Depends, Request
from authx import TokenPayload, RequestToken
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.db.models import User
from app.db.models.user import UserRole
from app.db.repository import Repository
from app.exceptions.auth import AuthError, TokenExpiredError
from app.routers.auth import security
from app.utils.role_verifier import RoleVerifier


async def validate_token_from_request(request: Request) -> TokenPayload:
    try:
        token: RequestToken = await security.get_access_token_from_request(request)
        token_payload: TokenPayload = security.verify_token(token, verify_csrf=False)
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


def require_role(required_role: UserRole):
    async def dependency(
            request: Request,
            session: AsyncSession = Depends(get_session)
    ) -> User:
        current_user = await get_current_user(request, session)
        await RoleVerifier(current_user).verify(required_role)
        return current_user

    return dependency
