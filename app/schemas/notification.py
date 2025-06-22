from pydantic import Field

from app.schemas.base import BaseSchema, BaseModelSchema
from app.db.models.notification import NotificationType


class NotificationBaseSchema(BaseSchema):
    notification_type: NotificationType
    text: str = Field(min_length=1, max_length=300)


class NotificationCreateSchema(NotificationBaseSchema):
    user_id: int = Field(gt=0)


class NotificationModelSchema(BaseModelSchema, NotificationBaseSchema):
    user_id: int = Field(gt=0)
