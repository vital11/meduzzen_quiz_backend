from pydantic import BaseModel, SecretStr, EmailStr


class SignUpRequestModel(BaseModel):
    email: str | EmailStr
    password: str | SecretStr


class SignInRequestModel(BaseModel):
    email: str | EmailStr
    password: str | SecretStr


class UserUpdateRequestModel(BaseModel):
    email: str | EmailStr
    password: str | SecretStr


class User(BaseModel):
    id: int
    email: str | EmailStr
    password: str | SecretStr
    is_active: bool = None

    class Config:
        orm_mode = True


class UsersListResponseModel(BaseModel):
    users: list[User] = []

