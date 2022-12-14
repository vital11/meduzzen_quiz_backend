from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user, get_current_active_superuser
from app.db.repositories.membership import MembershipRepository
from app.schemas.user import User
from app.schemas.membership import (Membership, MembershipCreate, MembershipParams,
                                    Member, MemberUpdate, CompanyMember, MemberCompany)


router = APIRouter(tags=['memberships'])


@router.post('/memberships/', response_model=Membership)
async def create_membership(
        payload: MembershipCreate, current_user: User = Depends(get_current_user)) -> Membership:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.create_membership(payload=payload)


@router.get('/memberships/all/', response_model=list[Membership])
async def read_all_memberships(
        current_user: User = Depends(get_current_active_superuser)) -> list[Membership]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_memberships_all()


@router.get('/memberships/', response_model=list[Membership])
async def read_memberships(
        q: MembershipParams = Depends(), current_user: User = Depends(get_current_user)) -> list[Membership]:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.get_memberships(q=q)


@router.delete('/memberships/{id}', response_model=Membership)
async def reject_membership(
        id: int, current_user: User = Depends(get_current_user)) -> Membership:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.delete_membership(id=id)


@router.post('/members/', response_model=Member)
async def accept_membership(
        payload: Membership, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.create_member(payload=payload)


@router.get('/members/companies/{company_id}', response_model=list[CompanyMember])
async def read_company_members(
        company_id: int, current_user: User = Depends(get_current_user)) -> list[CompanyMember]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_company_members(company_id=company_id)


@router.get('/members/users/{user_id}', response_model=list[MemberCompany])
async def read_member_companies(
        user_id: int, current_user: User = Depends(get_current_user)) -> list[MemberCompany]:
    membership_repo = MembershipRepository(db=database)
    return await membership_repo.get_member_companies(user_id=user_id)


@router.patch('/members/', response_model=Member)
async def toggle_member_admin_role(
        payload: MemberUpdate, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.update_member(payload=payload)


@router.delete('/members/{id}', response_model=Member)
async def delete_member(
        id: int, current_user: User = Depends(get_current_user)) -> Member:
    membership_repo = MembershipRepository(db=database, current_user=current_user)
    return await membership_repo.delete_member(id=id)
