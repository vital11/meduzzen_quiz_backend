from typing import List

from fastapi import APIRouter

from app.db.repositories.user import UserRepository
from app.schemas.user import User, UserCreate


router = APIRouter()


@router.post("/users/")
async def create_user(user: UserCreate):
    # TODO: -> User
    user_id = await UserRepository.add(**user.dict())
    return {"user_id": user_id}


@router.get("/users/{id}", response_model=User)
async def get_user(id_: int) -> User:
    user = await UserRepository.get(id_)
    return User(**user)


