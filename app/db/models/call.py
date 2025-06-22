from enum import StrEnum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum, Float, DateTime

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import Patient
    from app.db.models.team import Team


class CallStatus(StrEnum):
    NEW = "new"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    REJECTED = "rejected"


class CallType(StrEnum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    COMMON = "common"


class Call(Base):
    status: Mapped[CallStatus] = mapped_column(Enum(CallStatus, name="call_status"), nullable=False)
    type: Mapped[CallType] = mapped_column(Enum(CallType, name="call_type"), nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient",
                                              back_populates="calls",
                                              uselist=False,
                                              lazy="joined")
    team: Mapped["Team"] = relationship("Team",
                                        back_populates="calls",
                                        uselist=False,
                                        lazy="joined")
