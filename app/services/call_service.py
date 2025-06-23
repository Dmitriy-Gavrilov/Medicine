from enum import StrEnum
from sqlalchemy import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.call import Call, CallStatus, CallType

from app.schemas.call import CallCreateSchema, CallModelSchema, CallFullInfoSchema
from app.schemas.car import CarUpdateSchema
from app.schemas.notification import NotificationBaseSchema, NotificationType

from app.exceptions.call import CallNotFoundException, CallAlreadyExistsException, TeamCallNotFound
from app.schemas.team import CoordinatesSchema
from app.services.car_service import CarService

from app.services.user_service import UserService
from app.services.notification_service import NotificationService


class TroubleType(StrEnum):
    CAR_BROKEN = "Поломка автомобиля"
    HUMAN_FACTOR = "Человеческий фактор"
    EXTERNAL_FACTOR = "Внешний фактор"


class CallService:
    def __init__(self):
        self.repo: Repository = Repository(Call)
        self.user_service: UserService = UserService()
        self.notification_service: NotificationService = NotificationService()
        self.car_service: CarService = CarService()

    async def get_calls(self, session: AsyncSession):
        return await self.repo.get(session)

    async def get_new_calls(self, session: AsyncSession):
        calls = await self.repo.get_by_filters(session, status=CallStatus.NEW)
        priority = {
            CallType.CRITICAL: 0,
            CallType.IMPORTANT: 1,
            CallType.COMMON: 2,
        }
        calls.sort(key=lambda c: (priority[c.type], -c.date_time.timestamp()))
        return calls

    async def get_actual_calls(self, session: AsyncSession):
        return await self.repo.get_by_conditions(
            session,
            or_(Call.status == CallStatus.NEW, Call.status == CallStatus.ACCEPTED))
        # Почему работает преобразование в Pydantic-схему без явного указания

    async def get_call_by_id(self, call_id: int, session: AsyncSession) -> CallModelSchema:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()
        return CallModelSchema.from_orm(call)

    async def get_call_by_team_id(self, team_id: int, session: AsyncSession) -> Call:
        call = await self.repo.get_by_conditions(session,
                                                 and_(Call.team_id == team_id, Call.status == CallStatus.ACCEPTED))
        if not call:
            raise TeamCallNotFound()
        return call[0]

    async def get_call_full_info(self, call_id: int, session: AsyncSession) -> CallFullInfoSchema:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()
        return CallFullInfoSchema(
            id=call.id,
            reason=call.reason,
            address=call.address,
            date_time=call.date_time,
            status=call.status,
            type=call.type,
            patient_name=call.patient.name,
            patient_surname=call.patient.surname,
            patient_patronym=call.patient.patronym,
            patient_age=call.patient.age,
            patient_gender=call.patient.gender,
            created_at=call.created_at,
            updated_at=call.updated_at,
        )

    async def get_active_calls(self, session: AsyncSession) -> list:
        return [CallModelSchema.from_orm(c) for c in await self.repo.get_by_filters(session, status=CallStatus.NEW)]

    async def add_call(self, call: CallCreateSchema, session: AsyncSession) -> CallModelSchema:
        find_call = await self.repo.get_by_filters(session, **call.model_dump())
        if find_call:
            raise CallAlreadyExistsException()

        call_to_create = Call(**call.model_dump())
        created_call = await self.repo.create(session, call_to_create)

        # Уведомления диспетчерам
        dispatchers = await self.user_service.get_users_by_filters(session, role="dispatcher")
        dispatchers_ids = [d.id for d in dispatchers]
        await self.notification_service.notify_users(dispatchers_ids,
                                                     NotificationBaseSchema(notification_type=NotificationType.MESSAGE,
                                                                            text="Новый вызов"),
                                                     session)

        return CallModelSchema.from_orm(created_call)

    async def accept_call(self, call_id: int, team_id: int, session: AsyncSession) -> CallModelSchema:
        await self.repo.update(session, call_id, team_id=team_id, status=CallStatus.ACCEPTED)

        team = await self.user_service.team_service.get_team_by_id(team_id, session)
        await self.notification_service.notify_users([team.worker1_id, team.worker2_id, team.worker3_id],
                                                     NotificationBaseSchema(notification_type=NotificationType.MESSAGE,
                                                                            text="Назначен вызов"),
                                                     session)

        return CallModelSchema.from_orm(await self.repo.get_by_id(session, call_id))

    async def reject_call(self, call_id: int, session: AsyncSession) -> CallModelSchema:
        await self.repo.update(session, call_id, status=CallStatus.REJECTED)
        return CallModelSchema.from_orm(await self.repo.get_by_id(session, call_id))

    async def complete_call(self, call_id: int, session: AsyncSession):
        # Установка статуса завершен
        await self.repo.update(session, call_id, status=CallStatus.COMPLETED)

        # Уведомления диспетчерам
        dispatchers = await self.user_service.get_users_by_filters(session, role="dispatcher")
        dispatchers_ids = [d.id for d in dispatchers]
        await self.notification_service.notify_users(dispatchers_ids,
                                                     NotificationBaseSchema(notification_type=NotificationType.SUCCESS,
                                                                            text=f"Вызов {call_id} выполнен"),
                                                     session)
        # Перестановка бригады в точку вызова
        call = await self.repo.get_by_id(session, call_id)
        team = call.team
        await self.user_service.team_service.move_team(team.id, CoordinatesSchema(lat=call.lat, lon=call.lon), session)

        return call

    async def trouble_call(self, call_id: int, trouble_type: TroubleType,  session: AsyncSession) -> Call:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()

        await self.repo.update(session, call_id, status=CallStatus.NEW, team_id=None)

        if trouble_type == TroubleType.CAR_BROKEN:
            team_car = call.team.car
            await self.car_service.update_car(team_car.id, CarUpdateSchema(number=team_car.number, status=False), session)

            admins = await self.user_service.get_users_by_filters(session, role="admin")
            admins_ids = [d.id for d in admins]
            await self.notification_service.notify_users(admins_ids,
                                                         NotificationBaseSchema(
                                                             notification_type=NotificationType.TROUBLE,
                                                             text=f"Автомобиль {team_car.number} сломан"),
                                                         session)

        dispatchers = await self.user_service.get_users_by_filters(session, role="dispatcher")
        dispatchers_ids = [d.id for d in dispatchers]

        await self.notification_service.notify_users(dispatchers_ids,
                                                     NotificationBaseSchema(
                                                         notification_type=NotificationType.TROUBLE,
                                                         text=f"Проблема на вызове {call_id}: {trouble_type}"),
                                                     session)
        return await self.repo.get_by_id(session, call_id)
