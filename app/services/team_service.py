from sqlalchemy import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.call import CallStatus
from app.db.repository import Repository
from app.db.models.team import Team
from app.exceptions.team import TeamNotFoundException, TeamBusyException
from app.redis import redisService

from app.schemas.team import TeamCreateSchema, TeamModelSchema, CoordinatesSchema, TeamFullInfoSchema


class TeamService:
    def __init__(self):
        self.repo: Repository = Repository(Team)
        self.redisService = redisService

    async def get_teams(self, session: AsyncSession) -> list[Team]:
        return await self.repo.get_by_filters(session, is_deleted=False)

    async def get_full_info_teams(self, session: AsyncSession) -> list[TeamFullInfoSchema]:
        cached = await self.redisService.get_cache("teams:full_info")
        if cached:
            return [TeamFullInfoSchema(**team_dict) for team_dict in cached]

        teams = await self.get_teams(session)

        result = []
        for t in teams:
            worker1_fio = f"{t.worker1.surname} {t.worker1.name[0]}. {t.worker1.patronym[0]}."
            worker2_fio = f"{t.worker2.surname} {t.worker2.name[0]}. {t.worker2.patronym[0]}."
            worker3_fio = f"{t.worker3.surname} {t.worker3.name[0]}. {t.worker3.patronym[0]}."
            car_number = t.car.number
            is_busy = True if any(call.status == CallStatus.ACCEPTED for call in t.calls) else False
            team_full_info = TeamFullInfoSchema(
                id=t.id,
                worker1_fio=worker1_fio,
                worker2_fio=worker2_fio,
                worker3_fio=worker3_fio,
                car_number=car_number,
                is_busy=is_busy,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            result.append(team_full_info)

        await self.redisService.set_cache("teams:full_info", result, 180)

        return result

    async def get_team_by_id(self, team_id: int, session: AsyncSession) -> Team:
        return await self.repo.get_by_id(session, team_id)

    async def add_team(self, team: TeamCreateSchema, session: AsyncSession) -> TeamModelSchema:
        created_team = await self.repo.create(session, Team(**team.model_dump()))

        await self.redisService.del_cache("users:workers_free")
        await self.redisService.del_cache("teams:full_info")
        await self.redisService.del_cache("cars:free")

        return TeamModelSchema.model_validate(created_team)

    async def get_free_teams(self, session: AsyncSession) -> list[TeamModelSchema]:
        teams = await self.get_teams(session)
        return [
            TeamModelSchema.model_validate(t)
            for t in teams
            if not any(call.status == CallStatus.ACCEPTED for call in t.calls)
               and t.car.status
        ]

    async def get_team_by_user_id(self, user_id: int, session: AsyncSession) -> TeamModelSchema:
        cached = await self.redisService.get_cache(f"teams:by_user_id:{user_id}")
        if cached:
            return TeamModelSchema.model_validate(cached)

        teams = await self.repo.get_by_conditions(
            session,
            and_(
                Team.is_deleted == False,
                or_(
                    Team.worker1_id == user_id,
                    Team.worker2_id == user_id,
                    Team.worker3_id == user_id
                )
            )
        )
        if not teams:
            raise TeamNotFoundException()

        result = TeamModelSchema.model_validate(teams[0])

        await self.redisService.set_cache(f"teams:by_user_id:{user_id}", result, 300)

        return result

    async def move_team(self, team_id: int, new_coordinates: CoordinatesSchema, session: AsyncSession) -> Team:
        team = await self.repo.get_by_id(session, team_id)
        if not team:
            raise TeamNotFoundException()
        await self.repo.update(session, team_id, lat=new_coordinates.lat, lon=new_coordinates.lon)
        return await self.repo.get_by_id(session, team_id)

    async def set_is_moving_team(self, team_id: int, is_moving: bool, session: AsyncSession) -> None:
        await self.repo.update(session, team_id, is_moving=is_moving)

    async def delete_team(self, team_id: int, session: AsyncSession):
        team = await self.repo.get_by_id(session, team_id)
        if any(call.status == CallStatus.ACCEPTED for call in team.calls):
            raise TeamBusyException()

        await self.redisService.del_cache("users:workers_free")
        await self.redisService.del_cache("teams:full_info")

        await self.redisService.del_cache(f"teams:by_user_id:{team.worker1_id}")
        await self.redisService.del_cache(f"teams:by_user_id:{team.worker2_id}")
        await self.redisService.del_cache(f"teams:by_user_id:{team.worker3_id}")

        await self.redisService.del_cache("cars:free")

        return await self.repo.update(session, team_id, is_deleted=True)
