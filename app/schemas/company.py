from typing import Union
from pydantic import BaseModel


class CompanyIn(BaseModel):
    title: str
    description: Union[str, None] = None


class Company(BaseModel):
    id: int
    title: str
    description: Union[str, None] = None

    class Config:
        orm_mode = True



