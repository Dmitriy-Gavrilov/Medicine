from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.call import Call


class PatientGender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class Patient(Base):
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    patronym: Mapped[str] = mapped_column(nullable=False)
    gender: Mapped[PatientGender] = mapped_column(Enum(PatientGender, name="patient_gender"), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    calls: Mapped[list["Call"]] = relationship("Call",
                                               back_populates="patient",
                                               lazy="joined",
                                               cascade="delete")
