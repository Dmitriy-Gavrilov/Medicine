from fastapi import APIRouter

from app.schemas.patient import PatientCreateSchema, PatientModelSchema
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])
service = PatientService()


@router.get(path="/",
            summary="Получить всех пациентов",
            response_model=list[PatientModelSchema])
async def get_users():
    return await service.get_patients()


@router.get(path="/{user_id}",
            summary="Получить пациента по id",
            response_model=PatientModelSchema)
async def get_user_by_id(patient_id: int):
    return await service.get_patient_by_id(patient_id)


@router.post(path="/",
             summary="Создать пациента",
             response_model=PatientModelSchema)
async def create_user(new_patient: PatientCreateSchema):
    return await service.add_patient(new_patient)
