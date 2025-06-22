from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_manager import SessionManager

session_manager = SessionManager()


async def get_session() -> AsyncSession:
    async with session_manager.session_maker() as session:
        yield session
