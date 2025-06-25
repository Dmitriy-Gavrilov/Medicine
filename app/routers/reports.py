import csv
from datetime import datetime
from io import StringIO
from fastapi import Response, Depends

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.db.models import User
from app.db.models.user import UserRole
from app.schemas.report import TeamsLoadSchema, CallsStatisticsSchema
from app.services.report_service import ReportService
from app.utils.auth_utils import require_role

router = APIRouter(prefix="/reports", tags=["Reports"])
service = ReportService()


@router.get(path="/teams_load",
            summary="Получить нагрузку на бригады",
            response_model=TeamsLoadSchema)
async def get_teams_load(date_time_start: datetime,
                         session: AsyncSession = Depends(get_session),
                         user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.get_teams_load(date_time_start, session)


@router.get(path="/calls_statistics",
            summary="Получить статистику вызовов",
            response_model=CallsStatisticsSchema)
async def get_teams_load(date_time_start: datetime,
                         session: AsyncSession = Depends(get_session),
                         user: User = Depends(require_role(UserRole.ADMIN))):
    return await service.get_calls_statistics(date_time_start, session)


@router.get(path="/calls_report",
            summary="Получить детальный отчет о вызовах")
async def get_calls_report(date_time_start: datetime,
                           date_time_end: datetime,
                           session: AsyncSession = Depends(get_session),
                           user: User = Depends(require_role(UserRole.ADMIN))):
    report_data = await service.get_calls_reports(date_time_start, date_time_end, session)

    csv_buffer = StringIO()
    csv_buffer.write('\ufeff')
    writer = csv.DictWriter(csv_buffer, fieldnames=report_data[0].keys(), delimiter=";")
    writer.writeheader()
    writer.writerows(report_data)

    return Response(
        content=csv_buffer.getvalue().encode('utf-8'),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=calls_report.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )
