from typing import Optional
from pydantic import BaseModel, EmailStr, constr, validator

# from app.schemas.company import Company


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: constr(min_length=1, strip_whitespace=True)


# Properties to receive via API on update
class UserUpdate(BaseModel):
    password: Optional[constr(strip_whitespace=True)] = None
    name: Optional[constr(strip_whitespace=True)] = None

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


class UserInDBBase(UserBase):
    id: Optional[int] = None
    companies: list = []

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
