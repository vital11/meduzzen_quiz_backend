from databases import Database
from fastapi import HTTPException

from app.db.tables.user import users


class UserRepository:
    def __init__(self, db: Database, current_user=None, *args, **kwargs):
        self._db = db

    @property
    def db(self) -> Database:
        return self._db

    async def add(self, **user) -> int:
        query = users.insert().values(**user)
        user_id = await self.db.execute(query=query)
        return user_id

    async def get(self, id: int):
        query = users.select().where(users.c.id == id)
        row = await self.db.fetch_one(query=query)
        return row

    async def list(self) -> list:
        query = users.select()
        rows = await self.db.fetch_all(query=query)
        return rows

    async def delete(self, id: int) -> None:
        query = users.delete().where(users.c.id == id)
        await self.db.execute(query=query)

    async def update(self, id: int, payload) -> None:
        query = users.select().where(users.c.id == id)
        row = await self.db.fetch_one(query=query)
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        query = users.update().where(users.c.id == id).values(password=payload.password)
        await self.db.execute(query=query)

