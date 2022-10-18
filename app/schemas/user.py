from typing import Union
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserIn(UserBase):
    name: Union[str, None] = None
    is_active: bool


class User(UserBase):
    id: int
    name: Union[str, None] = None
    is_active: bool = None

    class Config:
        orm_mode = True
