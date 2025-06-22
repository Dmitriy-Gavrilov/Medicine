import time

from fastapi import APIRouter, Depends, Request

from app.db.models.user import UserRole, User
from app.schemas.user import UserModelSchema, UserCreateSchema, UserUpdateSchema

from app.services.user_service import UserService

from app.schemas.notification import NotificationModelSchema

from app.utils.auth_utils import require_role, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


@router.get(path="/check",
            summary="Проверка аутентификации",
            response_model=UserModelSchema)
async def check_auth(request: Request):
    return await get_current_user(request)


@router.get(path="/",
            summary="Получить всех пользователей",
            response_model=list[UserModelSchema])
async def get_users():
    return await service.get_users()


@router.get(path="/role/{user_role}",
            summary="Получить пользователей по роли",
            response_model=list[UserModelSchema])
async def get_users_by_role(user_role: UserRole):
    return await service.get_users_by_role(user_role)


@router.get(path="/workers/free",
            summary="Получить свободных работников",
            response_model=list[UserModelSchema])
async def get_free_workers():
    start = time.time()
    res = await service.get_free_workers()
    print("Workers:", time.time() - start)
    return res


@router.get(path="/{user_id}",
            summary="Получить пользователя по id",
            response_model=UserModelSchema)
async def get_user_by_id(user_id: int):
    return await service.get_user_by_id(user_id)


@router.post(path="/",
             summary="Создать пользователя",
             response_model=UserModelSchema,
             status_code=201)
async def create_user(new_user: UserCreateSchema,
                      user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.add_user(new_user)


@router.put(path="/{user_id}",
            summary="Обновить пользователя",
            response_model=UserModelSchema)
async def update_user(user_id: int, user_data: UserUpdateSchema):
    return await service.update_user(user_id, user_data)


@router.delete(path="/{user_id}",
               summary="Удалить пользователя",
               status_code=204)
async def delete_user(user_id: int):
    return await service.delete_user(user_id)


@router.get(path="/{user_id}/notifications",
            summary="Получить уведомления пользователя",
            response_model=list[NotificationModelSchema])
async def get_user_notifications(user_id: int):
    return await service.get_user_notifications(user_id)
