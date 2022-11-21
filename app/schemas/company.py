from typing import Optional

from pydantic import BaseModel, constr, validator
from app.schemas.user import User


class CompanyBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = False


# Properties to receive on item creation
class CompanyCreate(CompanyBase):
    name: constr(min_length=1, strip_whitespace=True)
    description: constr(min_length=1, strip_whitespace=True)


# Properties to receive on item update
class CompanyUpdate(CompanyBase):

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


# Properties shared by models stored in DB
class CompanyInDBBase(CompanyBase):
    id: Optional[int] = None
    owner_id: Optional[int] = None
    owner: Optional[User] = []

    class Config:
        orm_mode = True


# Properties to return to client
class Company(CompanyInDBBase):
    pass


# Properties stored in DB
class CompanyInDB(CompanyInDBBase):
    pass


