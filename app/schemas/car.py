from pydantic import Field

from app.schemas.base import BaseSchema, BaseModelSchema


class CarBaseSchema(BaseSchema):
    number: str = Field(pattern=r"^[А-Я]{1}\d{3}[А-Я]{2}$")


class CarCreateSchema(CarBaseSchema):
    pass


class CarUpdateSchema(CarBaseSchema):
    status: bool = True


class CarModelSchema(BaseModelSchema, CarUpdateSchema):
    pass
