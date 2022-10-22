from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/')
async def check_health():
    return JSONResponse(
        content={"status": "Working"},
        status_code=200
    )

