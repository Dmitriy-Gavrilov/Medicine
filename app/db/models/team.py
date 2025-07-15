from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Float, text

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.car import Car
    from app.db.models.call import Call
    from app.db.models.user import User


class Team(Base):
    worker1_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    worker2_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    worker3_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id"), nullable=False)

    lat: Mapped[float] = mapped_column(Float, nullable=False, default=59.907126)
    lon: Mapped[float] = mapped_column(Float, nullable=False, default=30.326599)

    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    is_moving: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)

    car: Mapped["Car"] = relationship("Car",
                                      back_populates="team",
                                      lazy="joined",
                                      uselist=False,
                                      cascade="delete")
    calls: Mapped[list["Call"]] = relationship("Call",
                                               back_populates="team",
                                               lazy="joined",
                                               cascade="delete")

    worker1: Mapped["User"] = relationship("User",
                                           back_populates="team_as_worker1",
                                           lazy="selectin",
                                           uselist=False,
                                           cascade="delete",
                                           primaryjoin="Team.worker1_id == User.id")
    worker2: Mapped["User"] = relationship("User",
                                           back_populates="team_as_worker2",
                                           lazy="selectin",
                                           uselist=False,
                                           cascade="delete",
                                           primaryjoin="Team.worker2_id == User.id")
    worker3: Mapped["User"] = relationship("User",
                                           back_populates="team_as_worker3",
                                           lazy="selectin",
                                           uselist=False,
                                           cascade="delete",
                                           primaryjoin="Team.worker3_id == User.id")
