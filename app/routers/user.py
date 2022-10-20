from pprint import pprint
from typing import List

from fastapi import APIRouter

from app.db.database import database
from app.db.repositories.user import UserRepository
from app.schemas.user import User, SignUpRequestModel, UserUpdateRequestModel

router = APIRouter()


@router.post("/users/", response_model=User, response_model_exclude={"password"})
async def create_user(user: SignUpRequestModel) -> User:
    user_repo = UserRepository(db=database)
    user_id = await user_repo.add(**user.dict())
    return User(**user.dict(), id=user_id)


@router.get("/users/{id}", response_model=User, response_model_exclude={"password"})
async def get_user(id: int) -> User:
    user_repo = UserRepository(db=database)
    user_record = await user_repo.get(id=id)
    return User(**user_record)


@router.get("/users", response_model=List[User], response_model_exclude={"password"})
async def get_users_list() -> List[User]:
    user_repo = UserRepository(db=database)
    user_records = await user_repo.list()
    return list(User(**user_record) for user_record in user_records)


@router.delete("/users/{id}")
async def delete_user(id: int) -> dict:
    user_repo = UserRepository(db=database)
    await user_repo.delete(id=id)
    return {"message": f"User(id={id}) has been deleted."}


@router.put("/users/{id}", response_model=User)
async def update_user(id: int, payload: UserUpdateRequestModel) -> User:
    user_repo = UserRepository(db=database)
    await user_repo.update(id=id, payload=payload)
    return User(**payload.dict(), id=id)

