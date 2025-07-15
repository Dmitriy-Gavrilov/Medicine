from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_manager import SessionManager

session_manager = SessionManager(engine_kwargs={"pool_size": 10})


async def get_session() -> AsyncSession:
    async with session_manager.session_maker() as session:
        yield session


@asynccontextmanager
async def get_manual_session():
    async with session_manager.session_maker() as session:
        yield session
