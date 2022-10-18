import sqlalchemy
from app.db.database import metadata


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean),
)


# class User:
#     @classmethod
#     async def get(cls, id):
#         query = users.select().where(users.c.id == id)
#         user = await db.fetch_one(query)
#         return user
#
#     @classmethod
#     async def create(cls, **user):
#         query = users.insert().values(**user)
#         user_id = await db.execute(query)
#         return user_id
