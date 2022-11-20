from typing import Optional

from pydantic import BaseModel, constr, validator


# Shared properties
class CompanyBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool]


# Properties to receive on item creation
class CompanyCreate(CompanyBase):
    name: constr(min_length=1, strip_whitespace=True)
    description: constr(min_length=1, strip_whitespace=True)
    is_private: bool = False


# Properties to receive on item update
class CompanyUpdate(CompanyBase):
    pass

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


# Properties shared by models stored in DB
class CompanyInDBBase(CompanyBase):
    id: Optional[int] = None
    name: str
    description: str
    owner_id: int
    is_private: bool

    class Config:
        orm_mode = True


# Properties to return to client
class Company(CompanyInDBBase):
    pass


# Properties stored in DB
class CompanyInDB(CompanyInDBBase):
    pass


# Many-to-Many Relationship
class AssociationTable(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class Admins(AssociationTable):
    pass


class Members(AssociationTable):
    pass
