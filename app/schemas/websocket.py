from enum import StrEnum

from app.schemas.base import BaseSchema
from app.schemas.call import CallModelSchema, CallFullInfoSchema
from app.schemas.team import TeamModelSchema, CoordinatesSchema


class EventType(StrEnum):
    NEW_CALL = "new_call"
    CALL_ACCEPTED = "call_accepted"
    CALL_REJECTED = "call_rejected"
    AVAILABLE_TEAM = "available_team"

    MOVE_STARTED = "move_started"
    MOVE_TEAM = "move_team"
    MOVE_FINISHED = "move_finished"
    ASSIGNED_CALL = "assigned_call"
    COMPLETED_CALL = "completed_call"
    TROUBLE_CALL = "trouble_call"


class BaseWSMessage(BaseSchema):
    event: EventType


class NewCallMessage(BaseWSMessage):
    call: CallModelSchema


class CallAcceptedMessage(BaseWSMessage):
    call_id: int
    team_id: int


class CallRejectedMessage(BaseWSMessage):
    call_id: int


class AvailableTeamMessage(BaseWSMessage):
    team: TeamModelSchema


class MoveStartedMessage(BaseWSMessage):
    pass


class MoveTeamMessage(BaseWSMessage):
    coordinates: CoordinatesSchema


class MoveFinishedMessage(BaseWSMessage):
    pass


class AssignedCallMessage(BaseWSMessage):
    call: CallFullInfoSchema


class CompletedCallMessage(BaseWSMessage):
    call_id: int


class TroubleCallMessage(BaseWSMessage):
    call_id: int
