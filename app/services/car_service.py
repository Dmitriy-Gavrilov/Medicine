from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.car import Car
from app.redis import redisService

from app.schemas.car import CarCreateSchema, CarModelSchema, CarUpdateSchema

from app.exceptions.car import CarAlreadyExistsException, CarNotFoundException, CarBusyException


class CarService:
    def __init__(self):
        self.repo: Repository = Repository(Car)
        self.redisService = redisService

    async def get_cars(self, session: AsyncSession) -> list[CarModelSchema]:
        cached = await self.redisService.get_cache("cars")
        if cached:
            return [CarModelSchema.model_validate(car_dict) for car_dict in cached]

        result = [CarModelSchema.model_validate(car) for car in await self.repo.get_by_filters(session, is_deleted=False)]

        await self.redisService.set_cache("cars", result, 300)

        return result

    async def get_free_cars(self, session: AsyncSession) -> list[CarModelSchema]:
        cached = await self.redisService.get_cache("cars:free")
        if cached:
            return [CarModelSchema.model_validate(car_dict) for car_dict in cached]

        cars = await self.repo.get_by_filters(session, is_deleted=False)
        result = [CarModelSchema.model_validate(c) for c in cars if not c.team and c.status]

        await self.redisService.set_cache("cars:free", result, 300)

        return result

    async def add_car(self, car: CarCreateSchema, session: AsyncSession) -> CarModelSchema:
        existing_car = await self.repo.get_by_filters(session, number=car.number, is_deleted=False)
        if existing_car:
            raise CarAlreadyExistsException()

        created_car = await self.repo.create(session, Car(**car.model_dump()))

        await self.redisService.del_cache("cars")
        await self.redisService.del_cache("cars:free")

        return CarModelSchema.model_validate(created_car)

    async def delete_car(self, car_id: int, session: AsyncSession):
        car = await self.repo.get_by_id(session, car_id)
        if not car:
            raise CarNotFoundException()
        if car.team and not car.team.is_deleted:
            raise CarBusyException()

        await self.redisService.del_cache("cars")
        await self.redisService.del_cache("cars:free")

        return await self.repo.update(session, car_id, is_deleted=True)

    async def update_car(self, car_id: int, car_data: CarUpdateSchema, session: AsyncSession) -> Car:
        existing_car = await self.repo.get_by_id(session, car_id)
        if existing_car.number == car_data.number and existing_car.status == car_data.status:
            raise CarAlreadyExistsException()

        await self.repo.update(session, car_id, **car_data.model_dump())

        await self.redisService.del_cache("cars")
        await self.redisService.del_cache("cars:free")

        return await self.repo.get_by_id(session, car_id)
