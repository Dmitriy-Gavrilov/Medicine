from app.db.repository import Repository
from app.db.models.user import User, UserRole

from app.schemas.user import UserModelSchema, UserCreateSchema, UserUpdateSchema

from app.exceptions.user import UserNotFoundException, UserAlreadyExistsException, WorkerBusyError
from app.services.team_service import TeamService

from app.utils.password_hasher import PasswordHasher

from app.schemas.notification import NotificationModelSchema


class UserService:
    def __init__(self):
        self.repo: Repository = Repository(User)
        self.team_service: TeamService = TeamService()

    async def __get_busy_workers(self) -> set:
        teams = await self.team_service.get_teams()
        busy_workers_ids = set()
        for team in teams:
            busy_workers_ids.add(team.worker1_id)
            busy_workers_ids.add(team.worker2_id)
            busy_workers_ids.add(team.worker3_id)
        return busy_workers_ids

    async def get_users(self):
        return await self.repo.get()

    async def get_users_by_filters(self, **filters):
        return await self.repo.get_by_filters(**filters)

    async def get_user_by_id(self, user_id) -> UserModelSchema:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return UserModelSchema.from_orm(user)

    async def get_users_by_role(self, role: UserRole) -> list[UserModelSchema]:
        users = await self.repo.get_by_filters(role=role)
        return [UserModelSchema.from_orm(user) for user in users]

    async def get_free_workers(self) -> list[User]:
        workers: list[User] = await self.repo.get_by_filters(role=UserRole.WORKER)

        busy_workers_ids = await self.__get_busy_workers()
        return [w for w in workers if w.id not in busy_workers_ids]

    async def add_user(self, user: UserCreateSchema) -> UserModelSchema:
        find_user = await self.repo.get_by_filters(login=user.login)
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
        created_user = await self.repo.create(user_to_create)
        return UserModelSchema.from_orm(created_user)

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if user.role == UserRole.WORKER and user.id in await self.__get_busy_workers():
            raise WorkerBusyError()

        return await self.repo.delete(user_id)

    async def update_user(self, user_id: int, user_data: UserUpdateSchema):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        await self.repo.update(user_id, **user_data.model_dump())

        return await self.repo.get_by_id(user_id)

    async def get_user_notifications(self, user_id: int) -> list[NotificationModelSchema]:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        return [NotificationModelSchema.from_orm(n) for n in user.notifications][::-1]
