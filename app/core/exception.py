import fastapi
from fastapi import HTTPException
from starlette import status


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotAuthorizedError(HTTPException):
    def __init__(self, detail: str = None):
        self.detail = detail
        super().__init__(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail=self.detail or "You are not allowed to access this endpoint",
        )


class NotFoundError(HTTPException):
    def __init__(self, obj_name: str = None, detail: str = None):
        self.obj_name = obj_name
        self.detail = detail
        super().__init__(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=self.detail or f"{self.obj_name or 'Object'} with this credentials does not exist",
        )


class UniqueError(HTTPException):
    def __init__(self, obj_name: str = None, detail: str = None):
        self.obj_name = obj_name
        self.detail = detail
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=self.detail or f"{self.obj_name or 'Object'} with this credentials already exist",
        )
