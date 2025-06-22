from app.db.repository import Repository
from app.db.models.patient import Patient

from app.schemas.patient import PatientCreateSchema, PatientModelSchema

from app.exceptions.patient import PatientNotFoundException


class PatientService:
    def __init__(self):
        self.repo: Repository = Repository(Patient)

    async def get_patients(self):
        return await self.repo.get()

    async def get_patient_by_id(self, patient_id) -> PatientModelSchema:
        patient = await self.repo.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException()
        return PatientModelSchema.from_orm(patient)

    async def add_patient(self, patient: PatientCreateSchema) -> PatientModelSchema:
        patient_to_create = Patient(**patient.model_dump())
        created_patient = await self.repo.create(patient_to_create)
        return PatientModelSchema.from_orm(created_patient)

    async def delete_patient(self, patient_id: int):
        patient = await self.repo.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException()
        return await self.repo.delete(patient_id)
