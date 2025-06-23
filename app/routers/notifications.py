from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()


@router.delete(path="/{notification_id}",
               summary="Удалить уведомление",
               status_code=204)
async def del_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    return await service.del_notification(notification_id, session)
