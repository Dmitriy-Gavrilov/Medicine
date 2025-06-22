from pydantic import BaseModel
from app.db.models.call import CallStatus


class TeamsLoadSchema(BaseModel):
    load: dict[int, int]


class CallsStatisticsSchema(BaseModel):
    statistics: dict[CallStatus, int]
