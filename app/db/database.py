import sqlalchemy
import aioredis
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

from app.core import settings


DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(bind=engine)
# Base.metadata.create_all(bind=engine)
Base = declarative_base(metadata=metadata)
session_maker = sessionmaker(bind=engine)


async def create_redis_client():
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.set("status", "Aioredis connected")
    value = await redis.get("status")
    print(value)
    return redis

