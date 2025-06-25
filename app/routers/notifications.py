from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.db.models import User
from app.db.models.user import UserRole
from app.services.notification_service import NotificationService
from app.utils.auth_utils import required_roles

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()


@router.delete(path="/{notification_id}",
               summary="Удалить уведомление",
               status_code=204)
async def del_notification(notification_id: int,
                           session: AsyncSession = Depends(get_session),
                           user: User = Depends(
                               required_roles([UserRole.ADMIN, UserRole.DISPATCHER, UserRole.WORKER]))):
    return await service.del_notification(notification_id, session)
