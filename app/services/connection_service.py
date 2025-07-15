from collections import defaultdict

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.websocket import (
    NewCallMessage,
    CallAcceptedMessage,
    CallRejectedMessage,
    AvailableTeamMessage,
    MoveTeamMessage,
    MoveFinishedMessage,
    AssignedCallMessage,
    CompletedCallMessage,
    TroubleCallMessage,
)
from app.services.team_service import TeamService
from logger import logger

DispatcherMessage = (
        NewCallMessage
        | CallAcceptedMessage
        | CallRejectedMessage
        | AvailableTeamMessage
)

WorkerMessage = (
        MoveTeamMessage
        | MoveFinishedMessage
        | AssignedCallMessage
        | CompletedCallMessage
        | TroubleCallMessage
)


class ConnectionService:
    def __init__(self):
        self.team_service = TeamService()

        self.dispatchers: set[WebSocket] = set()
        self.workers: dict[WebSocket, int] = defaultdict(int)
        self.teams: dict[int, set[WebSocket]] = defaultdict(set)

    async def handle_connect_dispatcher(self, ws: WebSocket) -> None:
        self.dispatchers.add(ws)

    async def handle_disconnect_dispatcher(self, ws: WebSocket) -> None:
        self.dispatchers.discard(ws)

    async def handle_connect_worker(self,
                                    ws: WebSocket,
                                    worker: User,
                                    session: AsyncSession) -> None:
        worker_team = await self.team_service.get_team_by_user_id(worker.id, session)
        self.workers[ws] = worker_team.id
        self.teams[worker_team.id].add(ws)

    async def handle_disconnect_worker(self, ws: WebSocket) -> None:
        self.teams[self.workers[ws]].discard(ws)
        del self.workers[ws]

    async def notify_dispatchers(self, message: DispatcherMessage) -> None:
        logger.info(f"WS SEND Dispatcher {message.event}")

        for d in self.dispatchers:
            try:
                await d.send_json(message.model_dump(mode="json"))
            except Exception:
                await self.handle_disconnect_dispatcher(d)

    async def notify_workers(self, team_id: int, message: WorkerMessage) -> None:
        logger.info(f"WS SEND Worker {message.event}")

        for ws in self.teams[team_id]:
            try:
                await ws.send_json(message.model_dump(mode="json"))
            except Exception:
                await self.handle_disconnect_worker(ws)


connection_service = ConnectionService()
