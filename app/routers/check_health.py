from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse

from app.db.database import create_redis_client
from app.core.verification import VerifyToken


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


@router.get("/auth0/public")
def check_auth0_public() -> dict:
    """No access token required to access this route"""
    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! "
                "You don't need to be authenticated to see this.")
    }
    return result


@router.get("/auth0/private")
def check_auth0_private(response: Response, token=Depends(HTTPBearer())) -> dict:
    """A valid access token is required to access this route"""
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return result
