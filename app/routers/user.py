from fastapi import APIRouter

from app.db.database import database
from app.db.repositories.user import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/users/", response_model=User)
async def create_user(payload: UserCreate) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.create(payload=payload)
    return user


@router.get("/users/{id}", response_model=User)
async def get_user(id: int) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.get(id=id)
    return user


@router.get("/users", response_model=list[User])
async def get_users_list() -> list[User]:
    user_repo = UserRepository(db=database)
    users = await user_repo.get_all()
    return users


@router.delete("/users/{id}", response_model=User)
async def delete_user(id: int) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.delete(id=id)
    return user


@router.put("/users/{id}", response_model=User)
async def update_user(id: int, payload: UserUpdate) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.update(id=id, payload=payload)
    return user
