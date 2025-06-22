from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.team import Team


class Car(Base):
    number: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)

    team: Mapped["Team"] = relationship("Team",
                                        back_populates="car",
                                        lazy="joined",
                                        uselist=False,
                                        cascade="delete")
