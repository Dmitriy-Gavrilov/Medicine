from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repository import Repository
from app.exceptions.auth import WrongLoginPasswordException, WrongRoleException, AuthError
from app.schemas.auth import AuthSchema
from app.schemas.user import UserModelSchema
from app.utils.password_hasher import PasswordHasher


class AuthService:
    def __init__(self):
        self.repo = Repository(User)

    async def check_user(self, auth: AuthSchema, session: AsyncSession) -> UserModelSchema:
        users = await self.repo.get_by_filters(session, login=auth.login)
        if not users:
            raise WrongLoginPasswordException()
        user = users[0]
        if not await PasswordHasher().verify_password(auth.password, user.password):
            raise WrongLoginPasswordException()
        if user.role != auth.role:
            raise WrongRoleException()
        return UserModelSchema.model_validate(user)

    async def get_user(self, user_id: int, session: AsyncSession) -> UserModelSchema:
        user = await self.repo.get_by_id(session, user_id)
        return UserModelSchema.model_validate(user)

    async def update_refresh_id(self, user_id: int, refresh_id: str, session: AsyncSession) -> None:
        return await self.repo.update(session, user_id, refresh_id=refresh_id)

    async def update_user_ip(self, user_id: int, user_ip: str, session: AsyncSession) -> None:
        return await self.repo.update(session, user_id, ip=user_ip)

    async def check_user_refresh(self, user_id: int, user_ip: str, refresh_id: str,
                                 session: AsyncSession) -> UserModelSchema:
        user = await self.repo.get_by_id(session, user_id)
        if user.ip == user_ip and user.refresh_id == refresh_id:
            return UserModelSchema.model_validate(user)
        # raise ошибки - неверный токен/ip
