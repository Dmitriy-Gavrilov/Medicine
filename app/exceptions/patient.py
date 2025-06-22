from app.exceptions.base import BaseCustomException


class PatientNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Пациент с таким id не найден")

