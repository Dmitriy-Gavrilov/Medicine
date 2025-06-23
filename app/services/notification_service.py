from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import Repository
from app.db.models.notification import Notification

from app.schemas.notification import NotificationCreateSchema, NotificationModelSchema, NotificationBaseSchema


class NotificationService:
    def __init__(self):
        self.repo: Repository = Repository(Notification)

    async def notify_user(self, note: NotificationCreateSchema, session: AsyncSession) -> NotificationModelSchema:
        created_note = await self.repo.create(session, Notification(**note.model_dump()))
        return NotificationModelSchema.from_orm(created_note)

    async def notify_users(self, ids: list[int], note: NotificationBaseSchema, session: AsyncSession) -> None:
        for i in ids:
            await self.notify_user(NotificationCreateSchema(text=note.text,
                                                            notification_type=note.notification_type,
                                                            user_id=i), session)

    async def del_notification(self, notification_id, session: AsyncSession):
        return await self.repo.delete(session, notification_id)
