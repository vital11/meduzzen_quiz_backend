from typing import List
from fastapi import APIRouter

from app.models.user import users
from app.schemas.user import User, UserCreate
from app.db.database import database


router = APIRouter()


@router.get("/users/", response_model=List[User])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)


@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    query = users.insert().values(email=user.email, password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}
