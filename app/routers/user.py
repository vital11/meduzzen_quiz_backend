from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user, get_current_active_superuser
from app.db.repositories.user import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(tags=["users"])


@router.post("/users/", response_model=User)
async def create_user(payload: UserCreate) -> User:
    user_repo = UserRepository(db=database)
    return await user_repo.create(payload=payload)


@router.get("/users/{id}", response_model=User)
async def read_user(id: int, current_user: User = Depends(get_current_user)) -> User:
    user_repo = UserRepository(db=database)
    return await user_repo.get(id=id)


@router.get("/users", response_model=list[User])
async def read_users(current_user: User = Depends(get_current_user)) -> list[User]:
    user_repo = UserRepository(db=database)
    return await user_repo.get_all()


@router.delete("/users/{id}", response_model=User)
async def delete_user(id: int, current_user: User = Depends(get_current_active_superuser)) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.get(id=id)
    return await user_repo.delete(current_user=user)


@router.patch("/users/{id}", response_model=User)
async def update_user(id: int, payload: UserUpdate, current_user: User = Depends(get_current_active_superuser)) -> User:
    user_repo = UserRepository(db=database)
    user = await user_repo.get(id=id)
    return await user_repo.update(payload=payload, current_user=user)


@router.get("/users/me/", response_model=User)
async def read_user_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/users/me/", response_model=User)
async def update_user_me(payload: UserUpdate, current_user: User = Depends(get_current_user)) -> User:
    user_repo = UserRepository(db=database)
    return await user_repo.update(payload=payload, current_user=current_user)


@router.delete("/users/me/", response_model=User)
async def delete_user_me(current_user: User = Depends(get_current_user)) -> User:
    user_repo = UserRepository(db=database)
    return await user_repo.delete(current_user=current_user)
