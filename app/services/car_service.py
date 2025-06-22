from app.db.repository import Repository
from app.db.models.car import Car

from app.schemas.car import CarCreateSchema, CarModelSchema, CarUpdateSchema

from app.exceptions.car import CarAlreadyExistsException, CarNotFoundException, CarBusyException


class CarService:
    def __init__(self):
        self.repo: Repository = Repository(Car)

    async def get_cars(self):
        return await self.repo.get_by_filters(is_deleted=False)

    async def get_free_cars(self) -> list[CarModelSchema]:
        cars = await self.get_cars()
        return [CarModelSchema.from_orm(c) for c in cars if not c.team and c.status]

    async def add_car(self, car: CarCreateSchema) -> CarModelSchema:
        existing_car = await self.repo.get_by_filters(number=car.number, is_deleted=False)
        if existing_car:
            raise CarAlreadyExistsException()

        created_car = await self.repo.create(Car(**car.model_dump()))
        return CarModelSchema.from_orm(created_car)

    async def delete_car(self, car_id: int):
        car = await self.repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundException()
        if car.team and not car.team.is_deleted:
            raise CarBusyException()

        return await self.repo.update(car_id, is_deleted=True)

    async def update_car(self, car_id: int, car_data: CarUpdateSchema) -> Car:
        existing_car = await self.repo.get_by_id(car_id)
        if existing_car.number == car_data.number and existing_car.status == car_data.status:
            raise CarAlreadyExistsException()

        await self.repo.update(car_id, **car_data.model_dump())

        return await self.repo.get_by_id(car_id)
