from pydantic import Field

from app.schemas.base import BaseSchema, BaseModelSchema
from app.db.models.patient import PatientGender


class PatientBaseSchema(BaseSchema):
    name: str = Field(min_length=1, max_length=20)
    surname: str = Field(min_length=1, max_length=20)
    patronym: str = Field(min_length=1, max_length=20)
    age: int = Field(gt=0, le=150)
    gender: PatientGender


class PatientCreateSchema(PatientBaseSchema):
    pass


class PatientModelSchema(BaseModelSchema, PatientBaseSchema):
    pass
