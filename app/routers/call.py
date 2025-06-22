from fastapi import APIRouter

from app.schemas.call import CallCreateSchema, CallModelSchema, CallFullInfoSchema
from app.services.call_service import CallService, TroubleType

router = APIRouter(prefix="/calls", tags=["Calls"])
service = CallService()


@router.get(path="/",
            summary="Получить все вызовы",
            response_model=list[CallModelSchema])
async def get_calls():
    return await service.get_calls()


@router.get(path="/new",
            summary="Получить новые вызовы",
            response_model=list[CallModelSchema])
async def get_new_calls():
    return await service.get_new_calls()


@router.get(path="/actual",
            summary="Получить актуальные вызовы",
            response_model=list[CallModelSchema])
async def get_new_calls():
    return await service.get_actual_calls()


@router.get(path="/{call_id}",
            summary="Получить вызов по id",
            response_model=CallModelSchema)
async def get_call_by_id(call_id: int):
    return await service.get_call_by_id(call_id)


@router.get(path="/by_teamId/{team_id}",
            summary="Получить вызов по id бригады",
            response_model=CallModelSchema)
async def get_call_by_team_id(team_id: int):
    return await service.get_call_by_team_id(team_id)


@router.get(path="/full_info/{call_id}",
            summary="Получить полную информацию о вызове",
            response_model=CallFullInfoSchema)
async def get_call_full_info(call_id: int):
    return await service.get_call_full_info(call_id)


@router.post(path="/",
             summary="Создать вызов",
             response_model=CallModelSchema)
async def create_call(new_call: CallCreateSchema):
    return await service.add_call(new_call)


@router.patch(path="/accept/{call_id}",
              summary="Принять вызов",
              response_model=CallModelSchema)
async def accept_call(call_id: int, team_id: int):
    return await service.accept_call(call_id, team_id)


@router.patch(path="/reject/{call_id}",
              summary="Отклонить вызов",
              response_model=CallModelSchema)
async def reject_call(call_id: int):
    return await service.reject_call(call_id)


@router.patch(path="/complete/{call_id}",
              summary="Завершить вызов",
              response_model=CallModelSchema)
async def complete_call(call_id: int):
    return await service.complete_call(call_id)


@router.patch(path="/trouble/{call_id}",
              summary="Сообщить о проблеме на вызове",
              response_model=CallModelSchema)
async def trouble_call(call_id: int, trouble_type: TroubleType):
    return await service.trouble_call(call_id, trouble_type)
