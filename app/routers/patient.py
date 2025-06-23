from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.schemas.patient import PatientCreateSchema, PatientModelSchema
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])
service = PatientService()


@router.get(path="/",
            summary="Получить всех пациентов",
            response_model=list[PatientModelSchema])
async def get_users(session: AsyncSession = Depends(get_session)):
    return await service.get_patients(session)


@router.get(path="/{user_id}",
            summary="Получить пациента по id",
            response_model=PatientModelSchema)
async def get_user_by_id(patient_id: int, session: AsyncSession = Depends(get_session)):
    return await service.get_patient_by_id(patient_id, session)


@router.post(path="/",
             summary="Создать пациента",
             response_model=PatientModelSchema)
async def create_user(new_patient: PatientCreateSchema, session: AsyncSession = Depends(get_session)):
    return await service.add_patient(new_patient, session)
