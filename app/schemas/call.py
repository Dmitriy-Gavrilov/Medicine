from datetime import datetime

from pydantic import Field, model_validator

from app.schemas.base import BaseSchema, BaseModelSchema
from app.db.models.call import CallStatus, CallType
from app.schemas.patient import PatientGender


class CallBaseSchema(BaseSchema):
    reason: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=80)
    date_time: datetime
    lat: float = Field(ge=59.7, le=60.2)
    lon: float = Field(ge=29.6, le=30.9)
    status: CallStatus
    type: CallType
    patient_id: int = Field(gt=0)
    team_id: int | None = Field(gt=0)

    # @model_validator(mode='after')
    # def remove_tzinfo(self) -> "CallBaseSchema":
    #     if self.date_time.tzinfo is not None:
    #         self.date_time = self.date_time.replace(tzinfo=None)
    #     return self


class CallCreateSchema(CallBaseSchema):
    pass


class CallModelSchema(BaseModelSchema, CallBaseSchema):
    pass


class CallFullInfoSchema(BaseModelSchema):
    reason: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=80)
    date_time: datetime
    status: CallStatus
    type: CallType
    patient_name: str = Field(min_length=1, max_length=20)
    patient_surname: str = Field(min_length=1, max_length=20)
    patient_patronym: str = Field(min_length=1, max_length=20)
    patient_age: int = Field(gt=0, le=150)
    patient_gender: PatientGender
    lat: float = Field(ge=59.7, le=60.2)
    lon: float = Field(ge=29.6, le=30.9)
