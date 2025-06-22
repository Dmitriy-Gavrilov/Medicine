from app.db.models.call import CallStatus
from app.db.repository import Repository
from app.db.models.team import Team
from app.exceptions.team import TeamNotFoundException, TeamBusyException

from app.schemas.team import TeamCreateSchema, TeamModelSchema, CoordinatesSchema, TeamFullInfoSchema


class TeamService:
    def __init__(self):
        self.repo: Repository = Repository(Team)

    async def get_teams(self) -> list[Team]:
        return await self.repo.get_by_filters(is_deleted=False)

    async def get_full_info_teams(self) -> list[TeamFullInfoSchema]:
        teams = await self.get_teams()

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

        return result

    async def get_team_by_id(self, team_id: int) -> Team:
        return await self.repo.get_by_id(team_id)

    async def add_team(self, team: TeamCreateSchema) -> TeamModelSchema:
        created_team = await self.repo.create(Team(**team.model_dump()))
        return TeamModelSchema.from_orm(created_team)

    async def get_free_teams(self) -> list[TeamModelSchema]:
        teams = await self.get_teams()
        return [
            TeamModelSchema.from_orm(t)
            for t in teams
            if not any(call.status == CallStatus.ACCEPTED for call in t.calls)
               and t.car.status
        ]

    async def get_team_by_user_id(self, user_id: int) -> Team:
        all_teams = await self.get_teams()
        for t in all_teams:
            if t.worker1_id == user_id or t.worker2_id == user_id or t.worker3_id == user_id:
                return t
        raise TeamNotFoundException()

    async def move_team(self, team_id: int, new_coordinates: CoordinatesSchema) -> Team:
        team = await self.repo.get_by_id(team_id)
        if not team:
            raise TeamNotFoundException()
        await self.repo.update(team_id, lat=new_coordinates.lat, lon=new_coordinates.lon)
        return await self.repo.get_by_id(team_id)

    async def delete_team(self, team_id: int):
        team = await self.repo.get_by_id(team_id)
        if any(call.status == CallStatus.ACCEPTED for call in team.calls):
            raise TeamBusyException()
        return await self.repo.update(team_id, is_deleted=True)
