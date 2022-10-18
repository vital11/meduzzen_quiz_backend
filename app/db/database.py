from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from databases import Database
import sqlalchemy
import aioredis

import settings

# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()


DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


async def create_redis_client():
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.set("status", "Aioredis connected")
    value = await redis.get("status")
    print(value)
    return redis
