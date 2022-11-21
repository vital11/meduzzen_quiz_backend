from typing import Optional
from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException, status
from sqlalchemy import desc

from app.models.user import users
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.core.verification import verify_password, get_password_hash


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    async def create(self, payload: UserCreate) -> User:
        query = users.insert().values(
            email=payload.email,
            name=payload.name,
            hashed_password=get_password_hash(payload.password),
            is_active=True,
            is_superuser=False
        ).returning(*users.c)
        user_dict: Record = await self.db.fetch_one(query=query)
        return User(**user_dict)

    async def get(self, id: int) -> Optional[User]:
        query = users.select().where(users.c.id == id).options()
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User does not exist in the system"
            )
        return User(**user_dict)

    async def get_all(self) -> list[User]:
        query = users.select().order_by(desc(users.c.id))
        users_data: list[Record] = await self.db.fetch_all(query=query)
        return [User(**data) for data in users_data]

    async def update(self, payload: UserUpdate, current_user: User) -> User:
        update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            return current_user
        if update_data.get("password") is not None:
            hashed_password = get_password_hash(update_data.get("password"))
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        query = users.update().where(users.c.id == current_user.id).values(**update_data).returning(*users.c)
        user_dict: Record = await self.db.fetch_one(query=query)
        return User(**user_dict)

    async def delete(self, current_user: User) -> User:
        query = users.delete().where(users.c.id == current_user.id).returning(*users.c)
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User does not exist in the system"
            )
        return User(**user_dict)

    async def get_by_email(self, email: str, is_private: Optional[bool] = False) -> UserInDB | User | None:
        query = users.select().where(users.c.email == email)
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            raise HTTPException(status_code=404, detail=f"User with email={email} not found.")
        return UserInDB(**user_dict) if is_private else User(**user_dict)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user_with_password: UserInDB = await self.get_by_email(email=email, is_private=True)
        if not user_with_password:
            return None
        if not verify_password(password, user_with_password.hashed_password):
            return None
        return User(**user_with_password.dict())

    async def get_or_create_by_email(self, payload: UserCreate) -> User:
        query = users.select().where(users.c.email == payload.email)
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            query = users.insert().values(
                email=payload.email,
                name=payload.email,
                hashed_password=get_password_hash(payload.password),
                is_active=True,
                is_superuser=False,
            ).returning(*users.c)
            user_dict: Record = await self.db.fetch_one(query=query)
        return User(**user_dict)
