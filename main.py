import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from app.db.dependencies import session_manager

from app.routers.user import router as users_router
from app.routers.patient import router as patients_router
from app.routers.call import router as calls_router
from app.routers.car import router as cars_router
from app.routers.team import router as teams_router
from app.routers.auth import router as auth_router
from app.routers.notifications import router as notifications_router
from app.routers.reports import router as reports_router
from app.routers.websocket import router as websockets_router

from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await session_manager.close()


app = FastAPI(lifespan=lifespan,
              debug=True,
              title="Medicine System")


@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()

    response: Response = await call_next(request)

    process_time = round(time.time() - start_time, 4)
    method = request.method
    path = request.url.path
    code = response.status_code

    logger.info(f"{method} {path} {code} {process_time}ms")

    return response


api_router = APIRouter(prefix="/api")

api_router.include_router(users_router)
api_router.include_router(patients_router)
api_router.include_router(calls_router)
api_router.include_router(cars_router)
api_router.include_router(teams_router)
api_router.include_router(auth_router)
api_router.include_router(notifications_router)
api_router.include_router(reports_router)
api_router.include_router(websockets_router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "https://127.0.0.1:3000", "https://localhost", "https://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app",
                host="localhost",
                ssl_certfile="localhost+1.pem",
                ssl_keyfile="localhost+1-key.pem")
