from app.exceptions.base import BaseCustomException


class CarNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Автомобиль с таким id не найден")


class CarAlreadyExistsException(BaseCustomException):
    def __init__(self):
        super().__init__(409, "Автомобиль уже существует")


class CarBusyException(BaseCustomException):
    def __init__(self):
        super().__init__(409, "Автомобиль занят бригадой")
