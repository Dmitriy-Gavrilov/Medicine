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
        return UserModelSchema.from_orm(user)
