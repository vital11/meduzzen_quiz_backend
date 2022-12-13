from fastapi import Depends, Response, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import datetime
from jwt import decode
from jose import jwt, JWTError


from app.db.database import database
from app.db.repositories.user import UserRepository
from app.schemas.token import TokenData
from app.schemas.user import User, UserCreate
from app.core.verification import VerifyToken
from app.core import settings


async def get_user_from_form(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user_repo = UserRepository(db=database)
    user = await user_repo.get_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_user_from_auth0(response: Response, token: str) -> User:
    payload = VerifyToken(token).verify()
    if payload.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return payload
    email: str = payload.get("https://example.com/email")
    token_data = TokenData(email=email)
    payload = UserCreate(
        email=token_data.email,
        password=str(datetime.now()),
    )
    user_repo = UserRepository(db=database)
    return await user_repo.get_or_create_by_email(payload=payload)


async def get_current_user(response: Response, token=Depends(HTTPBearer())) -> User:
    payload = decode(token.credentials, options={"verify_signature": False})
    if payload.get("aud"):
        return await get_user_from_auth0(token=token.credentials, response=response)
    return await get_user_from_form(token=token.credentials)


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
