from datetime import datetime

from sqlalchemy import and_, or_

from app.db.models import Call, Team, Patient, User
from app.db.models.call import CallStatus
from app.db.repository import Repository
from app.schemas.report import TeamsLoadSchema, CallsStatisticsSchema


class ReportService:
    def __init__(self):
        self.call_repo: Repository = Repository(Call)
        self.team_repo: Repository = Repository(Team)

    async def get_teams_load(self, date_time_start: datetime):
        teams = await self.team_repo.get()
        calls = await self.call_repo.get_by_conditions(Call.date_time >= date_time_start)

        load = {t.id: 0 for t in teams}

        for call in calls:
            if call.status == CallStatus.COMPLETED:
                load[call.team_id] += 1

        return TeamsLoadSchema(load=load)

    async def get_calls_statistics(self, date_time_start: datetime):
        calls = await self.call_repo.get_by_conditions(Call.date_time >= date_time_start)
        stats = {CallStatus.COMPLETED: 0,
                 CallStatus.REJECTED: 0}
        for call in calls:
            if call.status in (CallStatus.COMPLETED, CallStatus.REJECTED):
                stats[call.status] += 1

        return CallsStatisticsSchema(statistics=stats)

    async def get_calls_reports(self, date_time_start: datetime, date_time_end: datetime):
        calls: list[Call] = await self.call_repo.get_by_conditions(and_(and_(Call.date_time >= date_time_start,
                                                                             Call.date_time <= date_time_end),
                                                                        or_(Call.status == CallStatus.COMPLETED,
                                                                            Call.status == CallStatus.REJECTED)))
        calls.sort(key=lambda x: x.id)
        report = []
        for call in calls:
            if call.status == CallStatus.COMPLETED:
                team: Team = call.team
                workers: list[User] = [team.worker1, team.worker2, team.worker3]
                team_info = (f"Бригада {team.id}: {workers[0].surname} {workers[0].name} {workers[0].patronym},"
                             f" {workers[1].surname} {workers[1].name} {workers[1].patronym},"
                             f" {workers[2].surname} {workers[2].name} {workers[2].patronym},"
                             f" Автомобиль: {team.car.number}")
            else:
                team_info = "NULL"
            patient: Patient = call.patient
            data = {
                "id": call.id,
                "date_time": call.date_time.strftime("%d.%m.%Y %H:%M:%S"),
                "address": call.address,
                "patient_info": (f"{patient.surname} {patient.name} {patient.patronym},"
                                 f" {'М' if patient.gender.value == 'male' else 'Ж'}, {patient.age}"),
                "status": call.status.value,
                "team_info": team_info
            }
            report.append(data)

        if not report:
            report.append({"id": None,
                           "date_time": None,
                           "address": None,
                           "patient_info": None,
                           "status": None,
                           "team_info": None})
        return report
