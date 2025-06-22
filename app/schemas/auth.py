from pydantic import Field

from app.db.models.user import UserRole
from app.schemas.base import BaseSchema


class AuthSchema(BaseSchema):
    login: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=20)
    role: UserRole


class AuthResponseSchema(BaseSchema):
    access_token: str
