from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.user import User, UserRole

from app.schemas.user import UserModelSchema, UserCreateSchema, UserUpdateSchema

from app.exceptions.user import UserNotFoundException, UserAlreadyExistsException, WorkerBusyError
from app.services.notification_service import NotificationService
from app.services.team_service import TeamService

from app.utils.password_hasher import PasswordHasher

from app.schemas.notification import NotificationModelSchema

from app.redis import redisService


class UserService:
    def __init__(self):
        self.repo: Repository = Repository(User)
        self.team_service: TeamService = TeamService()
        self.notification_service: NotificationService = NotificationService()
        self.redisService = redisService

    async def __get_busy_workers(self, session: AsyncSession) -> set:
        teams = await self.team_service.get_teams(session)
        busy_workers_ids = set()
        for team in teams:
            busy_workers_ids.add(team.worker1_id)
            busy_workers_ids.add(team.worker2_id)
            busy_workers_ids.add(team.worker3_id)
        return busy_workers_ids

    async def get_users(self, session: AsyncSession):
        return await self.repo.get(session)

    async def get_users_by_filters(self, session: AsyncSession, **filters):
        return await self.repo.get_by_filters(session, **filters)

    async def get_user_by_id(self, user_id, session: AsyncSession) -> UserModelSchema:
        cached = await self.redisService.get_cache(f"users:{user_id}")
        if cached:
            return UserModelSchema(**cached)

        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException()

        result = UserModelSchema.from_orm(user)

        await self.redisService.set_cache(f"users:{user_id}", result, 180)

        return result

    async def get_users_by_role(self, role: UserRole, session: AsyncSession) -> list[UserModelSchema]:
        cached = await self.redisService.get_cache(f"users:{role}")
        if cached:
            return [UserModelSchema(**user_dict) for user_dict in cached]

        users = await self.repo.get_by_filters(session, role=role)
        result = [UserModelSchema.from_orm(user) for user in users]

        await self.redisService.set_cache(f"users:{role}", result, 180)

        return result

    async def get_free_workers(self, session: AsyncSession) -> list[UserModelSchema]:
        cached = await self.redisService.get_cache("users:workers_free")
        if cached:
            return [UserModelSchema(**user_dict) for user_dict in cached]

        workers: list[User] = await self.repo.get_by_filters(session, role=UserRole.WORKER)

        busy_workers_ids = await self.__get_busy_workers(session)
        result = [UserModelSchema.from_orm(w) for w in workers if w.id not in busy_workers_ids]

        await self.redisService.set_cache("users:workers_free", result, ex=180)

        return result

    async def add_user(self, user: UserCreateSchema, session: AsyncSession) -> UserModelSchema:
        find_user = await self.repo.get_by_filters(session, login=user.login)
        if find_user:
            raise UserAlreadyExistsException()

        hashed_password = await PasswordHasher.hash_password(user.password)
        user_to_create = User(
            login=user.login,
            password=hashed_password,
            role=user.role,
            name=user.name,
            surname=user.surname,
            patronym=user.patronym
        )
        created_user = await self.repo.create(session, user_to_create)

        await self.redisService.del_cache(f"users:{user.role}")

        if user.role == UserRole.WORKER:
            await self.redisService.del_cache("users:workers_free")

        return UserModelSchema.from_orm(created_user)

    async def delete_user(self, user_id: int, session: AsyncSession):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException()

        if user.role == UserRole.WORKER and user.id in await self.__get_busy_workers(session):
            raise WorkerBusyError()

        if user.role == UserRole.WORKER:
            await self.redisService.del_cache("users:workers_free")

        await self.redisService.del_cache(f"users:{user.role}")
        await self.redisService.del_cache(f"users:{user_id}")

        return await self.repo.delete(session, user_id)

    async def update_user(self, user_id: int, user_data: UserUpdateSchema, session: AsyncSession):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException()

        await self.repo.update(session, user_id, **user_data.model_dump())

        await self.redisService.del_cache(f"users:{user.role}")
        await self.redisService.del_cache(f"users:{user_id}")

        return await self.repo.get_by_id(session, user_id)

    async def get_user_notifications(self, user_id: int, session: AsyncSession) -> list[NotificationModelSchema]:
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException()

        return await self.notification_service.get_user_notifications(user_id, session)
