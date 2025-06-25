from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.db.models import User
from app.db.models.user import UserRole
from app.schemas.call import CallCreateSchema, CallModelSchema, CallFullInfoSchema
from app.services.call_service import CallService, TroubleType
from app.utils.auth_utils import require_role, required_roles

router = APIRouter(prefix="/calls", tags=["Calls"])
service = CallService()


@router.get(path="/",
            summary="Получить все вызовы",
            response_model=list[CallModelSchema])
async def get_calls(session: AsyncSession = Depends(get_session),
                    user: User = Depends(require_role(UserRole.DISPATCHER))):
    return await service.get_calls(session)


@router.get(path="/new",
            summary="Получить новые вызовы",
            response_model=list[CallModelSchema])
async def get_new_calls(session: AsyncSession = Depends(get_session),
                        user: User = Depends(require_role(UserRole.DISPATCHER))):
    return await service.get_new_calls(session)


@router.get(path="/actual",
            summary="Получить актуальные вызовы",
            response_model=list[CallModelSchema])
async def get_new_calls(session: AsyncSession = Depends(get_session),
                        user: User = Depends(require_role(UserRole.DISPATCHER))):
    return await service.get_actual_calls(session)


@router.get(path="/{call_id}",
            summary="Получить вызов по id",
            response_model=CallModelSchema)
async def get_call_by_id(call_id: int,
                         session: AsyncSession = Depends(get_session),
                         user: User = Depends(required_roles([UserRole.DISPATCHER, UserRole.WORKER]))):
    return await service.get_call_by_id(call_id, session)


@router.get(path="/by_teamId/{team_id}",
            summary="Получить вызов по id бригады",
            response_model=CallModelSchema)
async def get_call_by_team_id(team_id: int,
                              session: AsyncSession = Depends(get_session),
                              user: User = Depends(require_role(UserRole.WORKER))):
    return await service.get_call_by_team_id(team_id, session)


@router.get(path="/full_info/{call_id}",
            summary="Получить полную информацию о вызове",
            response_model=CallFullInfoSchema)
async def get_call_full_info(call_id: int,
                             session: AsyncSession = Depends(get_session),
                             user: User = Depends(required_roles([UserRole.DISPATCHER, UserRole.WORKER]))):
    return await service.get_call_full_info(call_id, session)


@router.post(path="/",
             summary="Создать вызов",
             response_model=CallModelSchema)
async def create_call(new_call: CallCreateSchema,
                      session: AsyncSession = Depends(get_session)):
    return await service.add_call(new_call, session)


@router.patch(path="/accept/{call_id}",
              summary="Принять вызов",
              response_model=CallModelSchema)
async def accept_call(call_id: int,
                      team_id: int,
                      session: AsyncSession = Depends(get_session),
                      user: User = Depends(require_role(UserRole.DISPATCHER))):
    return await service.accept_call(call_id, team_id, session)


@router.patch(path="/reject/{call_id}",
              summary="Отклонить вызов",
              response_model=CallModelSchema)
async def reject_call(call_id: int,
                      session: AsyncSession = Depends(get_session),
                      user: User = Depends(require_role(UserRole.DISPATCHER))):
    return await service.reject_call(call_id, session)


@router.patch(path="/complete/{call_id}",
              summary="Завершить вызов",
              response_model=CallModelSchema)
async def complete_call(call_id: int,
                        session: AsyncSession = Depends(get_session),
                        user: User = Depends(require_role(UserRole.WORKER))):
    return await service.complete_call(call_id, session)


@router.patch(path="/trouble/{call_id}",
              summary="Сообщить о проблеме на вызове",
              response_model=CallModelSchema)
async def trouble_call(call_id: int,
                       trouble_type: TroubleType,
                       session: AsyncSession = Depends(get_session),
                       user: User = Depends(require_role(UserRole.WORKER))):
    return await service.trouble_call(call_id, trouble_type, session)
