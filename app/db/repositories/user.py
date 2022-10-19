from app.db.database import database
from app.models.user import users


class UserRepository:

    @classmethod
    async def add(cls, **user):
        query = users.insert().values(**user)
        user_id = await database.execute(query)
        return user_id

    @classmethod
    async def get(cls, id_: int):
        query = users.select().where(users.c.id == id_)
        user = await database.fetch_one(query)
        return user
