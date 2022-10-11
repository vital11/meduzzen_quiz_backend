import fastapi

router = fastapi.APIRouter()


@router.get('/')
def health_check():
    return fastapi.responses.JSONResponse(
        content={"status": "Working"},
        status_code=200
    )
