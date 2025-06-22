from app.exceptions.base import BaseCustomException


class CallNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Вызов с таким id не найден")


class TeamCallNotFound(BaseCustomException):
    def __init__(self):
        super().__init__(404, "У бригады нет вызовов")


class CallAlreadyExistsException(BaseCustomException):
    def __init__(self):
        super().__init__(409, "Вызов уже существует")
