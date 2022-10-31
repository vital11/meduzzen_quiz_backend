import sqlalchemy
import aioredis
from databases import Database

from app.core import settings


DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


async def create_redis_client():
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.set("status", "Aioredis connected")
    value = await redis.get("status")
    print(value)
    return redis
