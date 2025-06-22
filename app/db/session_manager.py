from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.settings import settings


class SessionManager:
    def __init__(self, url: str = settings.get_db_url(), engine_kwargs: dict[str, Any] = None):
        self.engine = create_async_engine(url, **engine_kwargs) if engine_kwargs else create_async_engine(url)
        self.session_maker = async_sessionmaker(autocommit=False,
                                                autoflush=False,
                                                expire_on_commit=False,
                                                bind=self.engine)

    async def close(self):
        await self.engine.dispose()
