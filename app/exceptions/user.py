from app.exceptions.base import BaseCustomException


class UserNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(404, "Пользователь с таким id не найден")


class UserAlreadyExistsException(BaseCustomException):
    def __init__(self):
        super().__init__(409, "Пользователь уже существует")


class WorkerBusyError(BaseCustomException):
    def __init__(self):
        super().__init__(409, "Работник числится в бригаде")
