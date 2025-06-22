from app.exceptions.base import BaseCustomException


class AuthError(BaseCustomException):
    def __init__(self):
        super().__init__(401, "Требуется войти в систему")


class TokenExpiredError(BaseCustomException):
    def __init__(self):
        super().__init__(401, "Срок действия сеанса истек")


class WrongRoleException(BaseCustomException):
    def __init__(self):
        super().__init__(401, "Неверная роль")


class WrongLoginPasswordException(BaseCustomException):
    def __init__(self):
        super().__init__(401, "Неверные логин или пароль")


class AdminRoleRequired(BaseCustomException):
    def __init__(self):
        super().__init__(403, "Требуется роль администратора")


class DispatcherRoleRequired(BaseCustomException):
    def __init__(self):
        super().__init__(403, "Требуется роль диспетчера")


class WorkerRoleRequired(BaseCustomException):
    def __init__(self):
        super().__init__(403, "Требуется роль работника")
