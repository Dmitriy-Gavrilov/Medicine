import time
from typing import Generic, TypeVar, Type

from sqlalchemy import Result, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get(self, session: AsyncSession):
        res: Result = await session.execute(select(self.model))
        return res.unique().scalars().all()

    async def get_by_filters(self, session: AsyncSession, **filters):
        res: Result = await session.execute(select(self.model).filter_by(**filters))
        return res.unique().scalars().all()

    async def get_by_conditions(self, session: AsyncSession, *conditions):
        res: Result = await session.execute(select(self.model).where(*conditions))
        return res.unique().scalars().all()

    async def get_custom(self,
                         session: AsyncSession,
                         filters: dict = None,
                         conditions: list = None,
                         order_by: list = None,
                         limit: int = None,
                         offset: int = None):
        stmt = select(self.model)
        if filters: stmt = stmt.filter_by(**filters)
        if conditions: stmt = stmt.where(*conditions)
        if order_by: stmt = stmt.order_by(*order_by)
        if limit: stmt = stmt.limit(limit)
        if offset: stmt = stmt.offset(offset)

        res: Result = await session.execute(stmt)
        return res.unique().scalars().all()

    async def get_by_id(self, session: AsyncSession, id: int) -> T:
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
