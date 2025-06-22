from pydantic import Field

from app.schemas.base import BaseSchema, BaseModelSchema


class TeamBaseSchema(BaseSchema):
    worker1_id: int = Field(gt=0)
    worker2_id: int = Field(gt=0)
    worker3_id: int = Field(gt=0)
    car_id: int = Field(gt=0)


class TeamCreateSchema(TeamBaseSchema):
    pass


class TeamModelSchema(BaseModelSchema, TeamBaseSchema):
    lat: float = Field(ge=59.7, le=60.2)
    lon: float = Field(ge=29.6, le=30.9)


class TeamFullInfoSchema(BaseModelSchema):
    worker1_fio: str = Field(min_length=3, max_length=150)
    worker2_fio: str = Field(min_length=3, max_length=150)
    worker3_fio: str = Field(min_length=3, max_length=150)
    car_number: str = Field(pattern=r"^[А-Я]{1}\d{3}[А-Я]{2}$")
    is_busy: bool


class CoordinatesSchema(BaseSchema):
    lat: float = Field(ge=59.7, le=60.2)
    lon: float = Field(ge=29.6, le=30.9)
