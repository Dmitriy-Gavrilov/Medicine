from typing import Generic, TypeVar, Type

from sqlalchemy import Result, select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.settings import settings

T = TypeVar('T')


class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.engine = create_async_engine(settings.get_db_url(),
                                          echo=settings.echo)

        self.async_session_maker = async_sessionmaker(self.engine)

    async def get(self):
        async with self.async_session_maker() as session:
            res: Result = await session.execute(select(self.model))
            return res.unique().scalars().all()

    async def get_by_filters(self, **filters):
        async with self.async_session_maker() as session:
            res: Result = await session.execute(select(self.model).filter_by(**filters))
            return res.unique().scalars().all()

    async def get_by_conditions(self, *conditions):
        async with self.async_session_maker() as session:
            res: Result = await session.execute(select(self.model).where(*conditions))
            return res.unique().scalars().all()

    async def get_by_id(self, id: int) ->T:
        async with self.async_session_maker() as session:
            res: Result = await session.execute(select(self.model).filter_by(id=id))
            return res.scalars().first()

    async def create(self, new: T) -> T:
        async with self.async_session_maker() as session:
            try:
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return new
            except Exception as e:
                await session.rollback()
                raise e

    async def update(self, update_id: int, **new_values):
        async with self.async_session_maker() as session:
            try:
                await session.execute(update(self.model).where(self.model.id == update_id).values(**new_values))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def delete(self, del_id: int):
        async with self.async_session_maker() as session:
            try:
                await session.execute(delete(self.model).where(self.model.id == del_id))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
