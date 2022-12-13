import aioredis
from sqlalchemy.ext.declarative import declarative_base
from databases import Database

from app.core import settings


database = Database(settings.DATABASE_URL)
Base = declarative_base()


async def create_redis_client():
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.set("status", "Aioredis connected")
    value = await redis.get("status")
    print(value)
    return redis
