import asyncio
from collections import defaultdict
from enum import StrEnum
from sqlalchemy import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_manual_session
from app.db.repository import Repository
from app.db.models.call import Call, CallStatus, CallType
from app.redis import redisService

from app.schemas.call import CallCreateSchema, CallModelSchema, CallFullInfoSchema
from app.schemas.car import CarUpdateSchema
from app.schemas.notification import NotificationBaseSchema, NotificationType

from app.exceptions.call import CallNotFoundException, CallAlreadyExistsException, TeamCallNotFound
from app.schemas.team import CoordinatesSchema, TeamModelSchema
from app.schemas.websocket import NewCallMessage, EventType, CallAcceptedMessage, CallRejectedMessage, \
    AvailableTeamMessage, CompletedCallMessage, AssignedCallMessage, MoveTeamMessage, MoveFinishedMessage, \
    TroubleCallMessage, MoveStartedMessage
from app.services.car_service import CarService
from app.services.connection_service import connection_service, ConnectionService

from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.utils.routing import Router


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
        self.connection_service: ConnectionService = connection_service
        self.routing_service: Router = Router()
        self.redisService = redisService

        self.routes: dict[int, list[CoordinatesSchema]] = defaultdict(list)
        self.move_tasks: dict[int, asyncio.Task] = {}

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
        return CallModelSchema.model_validate(call)

    async def get_call_by_team_id(self, team_id: int, session: AsyncSession) -> CallModelSchema:
        cached = await self.redisService.get_cache(f"calls:by_team_id{team_id}")
        if cached:
            return CallModelSchema.model_validate(cached)

        call = await self.repo.get_by_conditions(session,
                                                 and_(Call.team_id == team_id, Call.status == CallStatus.ACCEPTED))
        if not call:
            raise TeamCallNotFound()

        result = CallModelSchema.model_validate(call[0])

        await self.redisService.set_cache(f"calls:by_team_id{team_id}", result, 180)

        return result

    async def get_call_full_info(self, call_id: int, session: AsyncSession) -> CallFullInfoSchema:
        cached = await self.redisService.get_cache(f"calls:full_info{call_id}")
        if cached:
            return CallFullInfoSchema.model_validate(cached)

        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()

        result = CallFullInfoSchema(
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
            lat=call.lat,
            lon=call.lon,
        )

        await self.redisService.set_cache(f"calls:full_info{call_id}", result, 240)

        return result

    async def get_active_calls(self, session: AsyncSession) -> list:
        return [CallModelSchema.model_validate(c) for c in await self.repo.get_by_filters(session, status=CallStatus.NEW)]

    async def add_call(self, call: CallCreateSchema, session: AsyncSession) -> CallModelSchema:
        find_call = await self.repo.get_by_filters(session, **call.model_dump())
        if find_call:
            raise CallAlreadyExistsException()

        call_to_create = Call(**call.model_dump())
        created_call = CallModelSchema.model_validate(await self.repo.create(session, call_to_create))

        # Уведомления диспетчерам
        dispatchers = await self.user_service.get_users_by_filters(session, role="dispatcher")
        dispatchers_ids = [d.id for d in dispatchers]
        await self.notification_service.notify_users(dispatchers_ids,
                                                     NotificationBaseSchema(notification_type=NotificationType.MESSAGE,
                                                                            text="Новый вызов"),
                                                     session)

        # Оповещение диспетчеров через WS
        await self.connection_service.notify_dispatchers(NewCallMessage(event=EventType.NEW_CALL,
                                                                        call=created_call))

        return created_call

    async def accept_call(self, call_id: int, team_id: int, session: AsyncSession) -> CallModelSchema:
        await self.repo.update(session, call_id, team_id=team_id, status=CallStatus.ACCEPTED)

        team = await self.user_service.team_service.get_team_by_id(team_id, session)
        await self.notification_service.notify_users([team.worker1_id, team.worker2_id, team.worker3_id],
                                                     NotificationBaseSchema(notification_type=NotificationType.MESSAGE,
                                                                            text="Назначен вызов"),
                                                     session)

        call = CallModelSchema.model_validate(await self.repo.get_by_id(session, call_id))

        await self.redisService.del_cache("teams:full_info")

        # Оповещение диспетчеров через WS
        await self.connection_service.notify_dispatchers(CallAcceptedMessage(event=EventType.CALL_ACCEPTED,
                                                                             call_id=call_id,
                                                                             team_id=team_id))

        # Оповещение работников через WS
        await self.connection_service.notify_workers(team_id, AssignedCallMessage(event=EventType.ASSIGNED_CALL,
                                                                                  call=(await self.get_call_full_info(
                                                                                      call_id, session))))

        return call

    async def reject_call(self, call_id: int, session: AsyncSession) -> CallModelSchema:
        await self.repo.update(session, call_id, status=CallStatus.REJECTED)

        # Оповещение диспетчеров через WS
        await self.connection_service.notify_dispatchers(CallRejectedMessage(event=EventType.CALL_REJECTED,
                                                                             call_id=call_id))

        await self.redisService.del_cache(f"calls:full_info{call_id}")

        return CallModelSchema.model_validate(await self.repo.get_by_id(session, call_id))

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

        # Оповещение диспетчеров через WS
        await self.connection_service.notify_dispatchers(AvailableTeamMessage(event=EventType.AVAILABLE_TEAM,
                                                                              team=TeamModelSchema.model_validate(
                                                                                  team)))

        # Оповещение работников через WS
        await self.connection_service.notify_workers(team.id, CompletedCallMessage(event=EventType.COMPLETED_CALL,
                                                                                   call_id=call_id))

        await self.redisService.del_cache("teams:full_info")
        await self.redisService.del_cache(f"calls:by_team_id{call.team_id}")
        await self.redisService.del_cache(f"calls:full_info{call_id}")

        return call

    async def trouble_call(self, call_id: int, trouble_type: TroubleType, session: AsyncSession) -> Call:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()

        await self.user_service.team_service.set_is_moving_team(call.team_id, False, session)
        if call.team_id in self.routes:
            del self.routes[call.team_id]
        task = self.move_tasks.pop(call.team_id, None)
        if task and not task.done():
            task.cancel()

        await self.redisService.del_cache("teams:full_info")
        await self.redisService.del_cache(f"calls:by_team_id{call.team_id}")

        await self.repo.update(session, call_id, status=CallStatus.NEW, team_id=None)

        if trouble_type == TroubleType.CAR_BROKEN:
            team_car = call.team.car
            await self.car_service.update_car(team_car.id, CarUpdateSchema(number=team_car.number, status=False),
                                              session)

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

        # Оповещение диспетчеров через WS
        await self.connection_service.notify_dispatchers(NewCallMessage(event=EventType.NEW_CALL,
                                                                        call=CallModelSchema.model_validate(
                                                                            call)))

        await self.connection_service.notify_dispatchers(AvailableTeamMessage(event=EventType.AVAILABLE_TEAM,
                                                                              team=TeamModelSchema.model_validate(
                                                                                  call.team)))

        # Оповещение работников через WS
        await self.connection_service.notify_workers(call.team.id, TroubleCallMessage(event=EventType.TROUBLE_CALL,
                                                                                      call_id=call_id))

        return await self.repo.get_by_id(session, call_id)

    async def get_call_route(self, call_id: int, session: AsyncSession) -> list[CoordinatesSchema]:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()
        team = call.team

        cached_route = self.routes[team.id]
        if cached_route:
            for i in range(len(cached_route)):
                if abs(cached_route[i].lat - team.lat) < 0.00005 and abs(cached_route[i].lon - team.lon) < 0.00005:
                    self.routes[team.id] = cached_route[i:]
                    return self.routes[team.id]

        route = await self.routing_service.get_route(CoordinatesSchema(lat=team.lat, lon=team.lon),
                                                     CoordinatesSchema(lat=call.lat, lon=call.lon))
        self.routes[team.id] = route
        return route

    async def start_move(self, call_id: int, session: AsyncSession) -> None:
        call = await self.repo.get_by_id(session, call_id)
        if not call:
            raise CallNotFoundException()

        await self.connection_service.notify_workers(call.team.id, MoveStartedMessage(event=EventType.MOVE_STARTED))

        task = asyncio.create_task(self.start_move_background(call_id))
        self.move_tasks[call.team_id] = task

    async def start_move_background(self, call_id: int) -> None:
        async with get_manual_session() as session:
            call = await self.repo.get_by_id(session, call_id)
            if not call:
                raise CallNotFoundException()
            team = call.team

            if team.is_moving:
                return

            await self.user_service.team_service.set_is_moving_team(team.id, True, session)
            for point in self.routes[team.id]:
                if not team.is_moving:
                    return

                await self.user_service.team_service.move_team(team.id, CoordinatesSchema(lat=point.lat, lon=point.lon),
                                                               session)
                await self.connection_service.notify_workers(team.id, MoveTeamMessage(event=EventType.MOVE_TEAM,
                                                                                      coordinates=point))
                await asyncio.sleep(0.25)

            await self.user_service.team_service.set_is_moving_team(team.id, False, session)
            await self.connection_service.notify_workers(team.id, MoveFinishedMessage(event=EventType.MOVE_FINISHED))

            del self.routes[team.id]
            self.move_tasks.pop(team.id, None)
