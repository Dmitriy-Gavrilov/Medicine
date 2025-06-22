from fastapi.exceptions import HTTPException


class BaseCustomException(HTTPException):
    def __init__(self, code: int, detail: str):
        super().__init__(status_code=code, detail=detail)
