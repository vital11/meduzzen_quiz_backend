from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user, get_current_active_superuser
from app.db.repositories.membership import MembershipRepository
from app.schemas.membership import Membership, MembershipApplication, MembershipQuery
from app.schemas.user import User


router = APIRouter(tags=['memberships'])


@router.post('/companies/memberships/', response_model=Membership)
async def create_membership(
        payload: MembershipApplication, current_user: User = Depends(get_current_user)
) -> Membership:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.create(payload=payload, current_user=current_user)


@router.get('/companies/memberships/all/', response_model=list[Membership])
async def read_all_memberships(current_user: User = Depends(get_current_active_superuser)) -> list[Membership]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_all()


@router.get('/companies/memberships/', response_model=list[Membership])
async def read_memberships(
        q: MembershipQuery = Depends(), current_user: User = Depends(get_current_user)
) -> list[Membership]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.filter(q=q, current_user=current_user)

