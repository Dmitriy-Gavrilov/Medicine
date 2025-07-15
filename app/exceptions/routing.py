from app.exceptions.base import BaseCustomException


class RoutingException(BaseCustomException):
    def __init__(self):
        super().__init__(400, "Ошибка получения маршрута")
