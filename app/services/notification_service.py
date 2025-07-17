from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.notification import Notification
from app.redis import redisService

from app.schemas.notification import NotificationCreateSchema, NotificationModelSchema, NotificationBaseSchema


class NotificationService:
    def __init__(self):
        self.repo: Repository = Repository(Notification)
        self.redisService = redisService

    async def notify_user(self, note: NotificationCreateSchema, session: AsyncSession) -> NotificationModelSchema:
        await self.redisService.del_cache(f"notifications:{note.user_id}")
        created_note = await self.repo.create(session, Notification(**note.model_dump()))
        return NotificationModelSchema.from_orm(created_note)

    async def notify_users(self, ids: list[int], note: NotificationBaseSchema, session: AsyncSession) -> None:
        for i in ids:
            await self.notify_user(NotificationCreateSchema(text=note.text,
                                                            notification_type=note.notification_type,
                                                            user_id=i), session)

    async def get_user_notifications(self, user_id: int, session: AsyncSession) -> list[NotificationModelSchema]:
        cached = await self.redisService.get_cache(f"notifications:{user_id}")
        if cached:
            return [NotificationModelSchema(**n) for n in cached]

        notifications = await self.repo.get_custom(session,
                                                   conditions=[Notification.user_id == user_id],
                                                   order_by=[desc(Notification.created_at)],
                                                   limit=15)
        result = [NotificationModelSchema.model_validate(n) for n in notifications]

        await self.redisService.set_cache(f"notifications:{user_id}", result, 120)

        return result

    async def del_notification(self, notification_id, session: AsyncSession):
        notification = await self.repo.get_by_id(session, notification_id)

        await self.redisService.del_cache(f"notifications:{notification.user_id}")

        return await self.repo.delete(session, notification_id)
