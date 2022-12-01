from typing import Optional
from pydantic import BaseModel, validator, EmailStr
import enum


class MembershipTypes(enum.Enum):
    invite = 'invite'
    request = 'request'


# Shared properties
class MembershipBase(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    membership_type: Optional[MembershipTypes] = None


# Properties to receive via API on creation
class MembershipApplication(MembershipBase):
    user_id: int
    company_id: int
    membership_type: MembershipTypes


class MembershipInDBBase(MembershipBase):
    membership_id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Membership(MembershipInDBBase):
    pass


class MembershipQuery(Membership):

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


# Shared properties
class MemberBase(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    is_admin: bool = False


# Properties to receive via API on update
class MemberUpdate(MemberBase):
    user_id: int
    company_id: int
    is_admin: bool


class MemberInDBBase(MemberBase):
    m_id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Member(MemberInDBBase):
    email: Optional[EmailStr]
