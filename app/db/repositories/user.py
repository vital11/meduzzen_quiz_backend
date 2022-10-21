from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException

from app.db.tables.user import users
from app.schemas.user import User, UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Database, current_user=None):
        self.db = db

    async def create(self, payload: UserCreate) -> User:
        query = users.insert().values(
            email=payload.email,
            name=payload.name,
            hashed_password=payload.password,
            is_active=payload.is_active,
            is_superuser=payload.is_superuser
        ).returning(*users.c)
        user_data: Record = await self.db.fetch_one(query=query)
        user = User(**user_data)
        return user

    async def get(self, id: int) -> User:
        query = users.select().where(users.c.id == id)
        user_data: Record = await self.db.fetch_one(query=query)
        user = User(**user_data)
        return user

    async def get_all(self) -> list[User]:
        query = users.select()
        users_data: list[Record] = await self.db.fetch_all(query=query)
        users_list = list(User(**data) for data in users_data)
        return users_list

    async def update(self, id: int, payload: UserUpdate) -> User:
        query = users.select().where(users.c.id == id)
        user_data: Record = await self.db.fetch_one(query=query)
        if user_data is None:
            raise HTTPException(status_code=404, detail=f"User with id={id} not found.")
        query = users.update().where(users.c.id == id).values(
            name=payload.name,
            hashed_password=payload.password
        ).returning(*users.c)
        user_data: Record = await self.db.fetch_one(query=query)
        print('============', dict(user_data))
        user = User(**user_data)
        return user

    async def delete(self, id: int) -> User:
        query = users.delete().where(users.c.id == id).returning(*users.c)
        user_data: Record = await self.db.fetch_one(query=query)
        user = User(**user_data)
        return user
