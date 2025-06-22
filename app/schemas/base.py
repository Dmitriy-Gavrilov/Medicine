from pydantic import BaseModel, Field

from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class BaseCreateSchema(BaseSchema):
    pass


class BaseModelSchema(BaseCreateSchema):
    id: int = Field(gt=0)

    created_at: datetime
    updated_at: datetime
