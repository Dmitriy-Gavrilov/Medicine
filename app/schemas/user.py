from pydantic import Field

from app.schemas.base import BaseSchema, BaseModelSchema
from app.db.models.user import UserRole


class UserBaseSchema(BaseSchema):
    login: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=20)
    name: str = Field(min_length=1, max_length=50)
    surname: str = Field(min_length=1, max_length=50)
    patronym: str = Field(min_length=1, max_length=50)
    role: UserRole


class UserCreateSchema(UserBaseSchema):
    pass


class UserUpdateSchema(BaseSchema):
    name: str = Field(min_length=1, max_length=50)
    surname: str = Field(min_length=1, max_length=50)
    patronym: str = Field(min_length=1, max_length=50)


class UserModelSchema(BaseModelSchema, UserBaseSchema):
    password: str = Field(min_length=60, max_length=60)
