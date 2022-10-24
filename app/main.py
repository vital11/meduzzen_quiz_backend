import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import settings
from app.db.database import database, create_redis_client
from app.routers import check_health, check_redis, user, login

app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
async def startup():
    await database.connect()
    await create_redis_client()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


if settings.CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


app.include_router(check_health.router)
app.include_router(check_redis.router)
app.include_router(user.router)
app.include_router(login.router)


if __name__ == '__main__':
    uvicorn.run('main:app', port=settings.SERVER_PORT, host=settings.SERVER_HOST, reload=True)
