from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user, get_current_active_superuser
from app.db.repositories.membership import MembershipRepository
from app.schemas.membership import Membership, MembershipCreate, MembershipQuery, Member, MemberUpdate
from app.schemas.user import User

router = APIRouter(tags=['memberships'])


@router.post('/companies/memberships/', response_model=Membership)
async def create_membership(
        payload: MembershipCreate, current_user: User = Depends(get_current_user)) -> Membership:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.create_membership(payload=payload)


@router.get('/companies/memberships/all/', response_model=list[Membership])
async def read_all_memberships(
        current_user: User = Depends(get_current_active_superuser)) -> list[Membership]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_memberships()


@router.get('/companies/memberships/', response_model=list[Membership])
async def read_memberships(
        q: MembershipQuery = Depends(), current_user: User = Depends(get_current_user)) -> list[Membership]:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.get_memberships_filtered(q=q)


@router.delete('/companies/memberships/{id}', response_model=Membership)
async def reject_membership(
        id: int, current_user: User = Depends(get_current_user)) -> Membership:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.delete_membership(id=id)


@router.post('/companies/members/', response_model=Member)
async def accept_membership(
        payload: Membership, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.create_member(payload=payload)


@router.get('/companies/{id}/members', response_model=list[Member])
async def read_members(
        id: int, current_user: User = Depends(get_current_user)) -> list[Member]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_members(company_id=id)


@router.patch('/companies/members/', response_model=Member)
async def toggle_member_admin_role(
        payload: MemberUpdate, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.update_member(payload=payload)


@router.delete('/companies/members/{id}', response_model=Member)
async def cancel_membership(
        id: int, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.delete_member(id=id)
