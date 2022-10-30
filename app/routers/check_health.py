from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.db.database import create_redis_client


router = APIRouter(tags=["check health"])


@router.get('/')
async def check_homepage():
    return JSONResponse(
        content={"status": "Working"},
        status_code=200
    )


@router.get('/redis')
async def check_redis():
    redis = await create_redis_client()
    value = await redis.get("status")
    return JSONResponse({"status": value})
