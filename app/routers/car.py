import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.db.models import User
from app.db.models.user import UserRole
from app.schemas.car import CarCreateSchema, CarModelSchema, CarUpdateSchema
from app.services.car_service import CarService
from app.utils.auth_utils import require_role

router = APIRouter(prefix="/cars", tags=["Cars"])
service = CarService()


@router.get(path="/",
            summary="Получить все автомобили",
            response_model=list[CarModelSchema])
async def get_cars(session: AsyncSession = Depends(get_session),
                   user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.get_cars(session)


@router.get(path="/free",
            summary="Получить свободные автомобили",
            response_model=list[CarModelSchema])
async def get_free_cars(session: AsyncSession = Depends(get_session),
                        user: User = Depends(require_role(UserRole.ADMIN))):
    res = await service.get_free_cars(session)
    return res


@router.post(path="/",
             summary="Добавить автомобиль",
             response_model=CarModelSchema,
             status_code=201)
async def create_car(new_car: CarCreateSchema,
                     session: AsyncSession = Depends(get_session),
                     user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.add_car(new_car, session)


@router.delete(path="/{car_id}",
               summary="Удалить автомобиль",
               status_code=204)
async def delete_car(car_id: int,
                     session: AsyncSession = Depends(get_session),
                     user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.delete_car(car_id, session)


@router.put(path="/{car_id}",
            summary="Обновить данные об автомобиле",
            response_model=CarModelSchema)
async def update_car(car_id: int,
                     car_data: CarUpdateSchema,
                     session: AsyncSession = Depends(get_session),
                     user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.update_car(car_id, car_data, session)
