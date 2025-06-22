from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class NotificationType(StrEnum):
    TROUBLE = "trouble"
    SUCCESS = "success"
    MESSAGE = "message"


class Notification(Base):
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name="notification_type"),
                                                                nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User",
                                        back_populates="notifications",
                                        uselist=False,
                                        lazy="joined")
