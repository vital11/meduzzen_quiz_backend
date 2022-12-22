from typing import Any

from fastapi import Depends, Response, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import datetime
from jwt import decode
from jose import jwt, JWTError

from app.core.exception import NotAuthorizedError
from app.db.database import database
from app.db.repositories.membership import MembershipRepository
from app.db.repositories.user import UserRepository
from app.schemas.membership import IsMemberCommons
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


def get_current_active_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def common_params(
        q: str | None = None,
        user_id: int | None = None,
        id: int | None = None,
        comp_id: int | None = None,
        company_id: int | None = None,
        payload: dict | None = None) -> IsMemberCommons:
    try:
        company_id = id or company_id or comp_id or payload.get('comp_id') or payload.get('company_id')
    except (TypeError, AttributeError):
        pass
    return IsMemberCommons(q=q, user_id=user_id, company_id=company_id)


async def get_current_member_user(
        current_user: User = Depends(get_current_user),
        commons: IsMemberCommons = Depends(common_params)) -> User:
    member_repo = MembershipRepository(db=database, current_user=current_user)
    if not await member_repo.is_member(company_id=commons.company_id, user_id=current_user.id):
        raise NotAuthorizedError(f'You are not the member of the Company')
    return current_user


async def get_current_admin_user(
        current_user: User = Depends(get_current_user),
        commons: IsMemberCommons = Depends(common_params)) -> User:
    member_repo = MembershipRepository(db=database, current_user=current_user)
    if not await member_repo.is_admin(company_id=commons.company_id, user_id=current_user.id):
        raise NotAuthorizedError(f'You are not the admin of the Company')
    return current_user


async def get_current_owner_user(
        current_user: User = Depends(get_current_user),
        commons: IsMemberCommons = Depends(common_params)) -> User:
    member_repo = MembershipRepository(db=database, current_user=current_user)
    if not await member_repo.is_owner(company_id=commons.company_id, user_id=current_user.id):
        raise NotAuthorizedError(f'You are not the owner of the Company')
    return current_user
