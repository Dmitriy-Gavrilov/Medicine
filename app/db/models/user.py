from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.notification import Notification
    from app.db.models.team import Team


class UserRole(StrEnum):
    DISPATCHER = "dispatcher"
    WORKER = "worker"
    ADMIN = "admin"


class User(Base):
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    patronym: Mapped[str] = mapped_column(nullable=False)

    notifications: Mapped[list["Notification"]] = relationship("Notification",
                                                               back_populates="user",
                                                               lazy="joined",
                                                               cascade="delete")
    team_as_worker1: Mapped["Team"] = relationship("Team",
                                                   foreign_keys="[Team.worker1_id]",
                                                   back_populates="worker1",
                                                   lazy="joined")

    team_as_worker2: Mapped["Team"] = relationship("Team",
                                                   foreign_keys="[Team.worker2_id]",
                                                   back_populates="worker2",
                                                   lazy="joined")

    team_as_worker3: Mapped["Team"] = relationship("Team",
                                                   foreign_keys="[Team.worker3_id]",
                                                   back_populates="worker3",
                                                   lazy="joined")
