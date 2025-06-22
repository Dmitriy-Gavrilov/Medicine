from typing import Generic, TypeVar, Type

from sqlalchemy import Result, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get(self, session: AsyncSession):
        async with session:
            res: Result = await session.execute(select(self.model))
            return res.unique().scalars().all()

    async def get_by_filters(self, session: AsyncSession, **filters):
        async with session:
            res: Result = await session.execute(select(self.model).filter_by(**filters))
            return res.unique().scalars().all()

    async def get_by_conditions(self, session: AsyncSession, *conditions):
        async with session:
            res: Result = await session.execute(select(self.model).where(*conditions))
            return res.unique().scalars().all()

    async def get_by_id(self, session: AsyncSession, id: int) -> T:
        async with session:
            res: Result = await session.execute(select(self.model).filter_by(id=id))
            return res.scalars().first()

    async def create(self, session: AsyncSession, new: T) -> T:
        async with session:
            try:
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return new
            except Exception as e:
                await session.rollback()
                raise e

    async def update(self, session: AsyncSession, update_id: int, **new_values):
        async with session:
            try:
                await session.execute(update(self.model).where(self.model.id == update_id).values(**new_values))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def delete(self, session: AsyncSession, del_id: int):
        async with session:
            try:
                await session.execute(delete(self.model).where(self.model.id == del_id))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
