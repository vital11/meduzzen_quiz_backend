from datetime import datetime
from functools import partial
from typing import Optional

from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException

from app.db.tables.user import users
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.core.verification import verify_password, get_password_hash


class UserRepository:
    def __init__(self, db: Database, current_user=None):
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
        user = User(**user_dict)
        return user

    async def get(self, id: int) -> User:
        query = users.select().where(users.c.id == id)
        user_dict: Record = await self.db.fetch_one(query=query)
        user = User(**user_dict)
        return user

    async def get_all(self) -> list[User]:
        query = users.select()
        users_data: list[Record] = await self.db.fetch_all(query=query)
        users_list = list(User(**data) for data in users_data)
        return users_list

    async def update(self, id: int, payload: UserUpdate) -> User:
        query = users.select().where(users.c.id == id)
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            raise HTTPException(status_code=404, detail=f"User with id={id} not found.")
        query = users.update().where(users.c.id == id).values(
            name=payload.name,
            hashed_password=get_password_hash(payload.password)
        ).returning(*users.c)
        user_dict: Record = await self.db.fetch_one(query=query)
        user = User(**user_dict)
        return user

    async def delete(self, id: int) -> User:
        query = users.delete().where(users.c.id == id).returning(*users.c)
        user_dict: Record = await self.db.fetch_one(query=query)
        user = User(**user_dict)
        return user

    async def get_by_email(self, email: str, is_private: Optional[bool] = False) -> UserInDB | User | None:
        query = users.select().where(users.c.email == email)
        user_dict: Record = await self.db.fetch_one(query=query)
        if user_dict is None:
            raise HTTPException(status_code=404, detail=f"User with email={email} not found.")
        user = UserInDB(**user_dict) if is_private else User(**user_dict)
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user_with_password: UserInDB = await self.get_by_email(email=email, is_private=True)
        if not user_with_password:
            return None
        if not verify_password(password, user_with_password.hashed_password):
            return None
        user = User(**user_with_password.dict())
        return user

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
        user = User(**user_dict)
        return user
