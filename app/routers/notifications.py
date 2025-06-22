from fastapi import APIRouter

from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()


@router.delete(path="/{notification_id}",
               summary="Удалить уведомление",
               status_code=204)
async def del_notification(notification_id: int):
    return await service.del_notification(notification_id)
