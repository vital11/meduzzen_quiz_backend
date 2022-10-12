import fastapi
import uvicorn

from app.routers import home

app = fastapi.FastAPI()


def configure():
    configure_routing()


def configure_routing():
    app.include_router(home.router)


if __name__ == '__main__':
    configure()
    uvicorn.run('main:app', port=8000, host='127.0.0.1', reload=True)
else:
    configure()

