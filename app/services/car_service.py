from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.car import Car

from app.schemas.car import CarCreateSchema, CarModelSchema, CarUpdateSchema

from app.exceptions.car import CarAlreadyExistsException, CarNotFoundException, CarBusyException


class CarService:
    def __init__(self):
        self.repo: Repository = Repository(Car)

    async def get_cars(self, session: AsyncSession):
        return await self.repo.get_by_filters(session, is_deleted=False)

    async def get_free_cars(self, session: AsyncSession) -> list[CarModelSchema]:
        cars = await self.get_cars(session)
        return [CarModelSchema.from_orm(c) for c in cars if not c.team and c.status]

    async def add_car(self, car: CarCreateSchema, session: AsyncSession) -> CarModelSchema:
        existing_car = await self.repo.get_by_filters(session, number=car.number, is_deleted=False)
        if existing_car:
            raise CarAlreadyExistsException()

        created_car = await self.repo.create(session, Car(**car.model_dump()))
        return CarModelSchema.from_orm(created_car)

    async def delete_car(self, car_id: int, session: AsyncSession):
        car = await self.repo.get_by_id(session, car_id)
        if not car:
            raise CarNotFoundException()
        if car.team and not car.team.is_deleted:
            raise CarBusyException()

        return await self.repo.update(session, car_id, is_deleted=True)

    async def update_car(self, car_id: int, car_data: CarUpdateSchema, session: AsyncSession) -> Car:
        existing_car = await self.repo.get_by_id(session, car_id)
        if existing_car.number == car_data.number and existing_car.status == car_data.status:
            raise CarAlreadyExistsException()

        await self.repo.update(session, car_id, **car_data.model_dump())

        return await self.repo.get_by_id(session, car_id)
