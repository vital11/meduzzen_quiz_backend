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
class MembershipCreate(MembershipBase):
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


class MembershipParams(Membership):

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


class Member(MemberInDBBase):
    pass


# Additional properties to return via API
class CompanyMember(MemberInDBBase):
    email: Optional[EmailStr]


class MemberCompany(MemberInDBBase):
    comp_name: Optional[str]


class MemberList(BaseModel):
    members: Optional[list[int]]
    admins: Optional[list[int]]
    owner: int
