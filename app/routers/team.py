from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.schemas.team import TeamCreateSchema, TeamModelSchema, CoordinatesSchema, TeamFullInfoSchema
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])
service = TeamService()


@router.get(path="/",
            summary="Получить все бригады",
            response_model=list[TeamModelSchema])
async def get_teams(session: AsyncSession = Depends(get_session)):
    return await service.get_teams(session)


@router.get(path="/full_info",
            summary="Получить полную информацию о бригадах",
            response_model=list[TeamFullInfoSchema])
async def get_full_info_teams(session: AsyncSession = Depends(get_session)):
    return await service.get_full_info_teams(session)


@router.get(path="/free",
            summary="Получить свободные бригады",
            response_model=list[TeamModelSchema])
async def get_free_teams(session: AsyncSession = Depends(get_session)):
    return await service.get_free_teams(session)


@router.get(path="/by_userId/{user_id}",
            summary="Получить бригаду работника",
            response_model=TeamModelSchema)
async def get_team_by_user_id(user_id: int, session: AsyncSession = Depends(get_session)):
    return await service.get_team_by_user_id(user_id, session)


@router.post(path="/",
             summary="Добавить бригаду",
             response_model=TeamModelSchema,
             status_code=201)
async def create_team(new_team: TeamCreateSchema, session: AsyncSession = Depends(get_session)):
    return await service.add_team(new_team, session)


@router.delete(path="/{team_id}",
               summary="Удалить бригаду",
               status_code=204)
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    return await service.delete_team(team_id, session)


@router.patch(path="/move",
              summary="Обновить местоположение бригады",
              response_model=TeamModelSchema)
async def move_team(team_id: int, new_coordinates: CoordinatesSchema, session: AsyncSession = Depends(get_session)):
    return await service.move_team(team_id, new_coordinates, session)
