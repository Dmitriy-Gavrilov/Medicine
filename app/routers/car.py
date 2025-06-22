import time

from fastapi import APIRouter

from app.schemas.car import CarCreateSchema, CarModelSchema, CarUpdateSchema
from app.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])
service = CarService()


@router.get(path="/",
            summary="Получить все автомобили",
            response_model=list[CarModelSchema])
async def get_cars():
    return await service.get_cars()


@router.get(path="/free",
            summary="Получить свободные автомобили",
            response_model=list[CarModelSchema])
async def get_free_cars():
    start = time.time()
    res = await service.get_free_cars()
    print("Cars", time.time() - start)
    return res


@router.post(path="/",
             summary="Добавить автомобиль",
             response_model=CarModelSchema,
             status_code=201)
async def create_car(new_car: CarCreateSchema):
    return await service.add_car(new_car)


@router.delete(path="/{car_id}",
               summary="Удалить автомобиль",
               status_code=204)
async def delete_car(car_id: int):
    return await service.delete_car(car_id)


@router.put(path="/{car_id}",
            summary="Обновить данные об автомобиле",
            response_model=CarModelSchema)
async def update_car(car_id: int, car_data: CarUpdateSchema):
    return await service.update_car(car_id, car_data)
