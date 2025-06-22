from app.exceptions.base import BaseCustomException


class TeamNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Бригада не найдена")


class TeamBusyException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Бригада находится на вызове")
