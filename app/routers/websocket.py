import asyncio

from fastapi import APIRouter, Depends, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.db.dependencies import get_manual_session
from app.db.models.user import UserRole, User
from app.services.connection_service import connection_service

from app.utils.auth_utils import require_role_ws

from logger import logger

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket(path="/dispatcher")
async def connect_dispatcher(ws: WebSocket,
                             dispatcher: User = Depends(require_role_ws(UserRole.DISPATCHER))):
    await ws.accept()
    logger.info(f"WS CONNECT Dispatcher {dispatcher.id}")
    await connection_service.handle_connect_dispatcher(ws)
    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=180)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        logger.info(f"WS DISCONNECT Dispatcher {dispatcher.id}")
        await connection_service.handle_disconnect_dispatcher(ws)


@router.websocket(path="/worker")
async def connect_worker(ws: WebSocket,
                         worker: User = Depends(require_role_ws(UserRole.WORKER))):
    await ws.accept()
    logger.info(f"WS CONNECT Worker {worker.id}")
    async with get_manual_session() as session:
        await connection_service.handle_connect_worker(ws, worker, session)

    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=180)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        logger.info(f"WS DISCONNECT Worker {worker.id}")
        await connection_service.handle_disconnect_worker(ws)
