from typing import Optional

from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update, or_
from sqlalchemy.orm import joinedload

from app.core.exception import NotAuthorizedError, NotFoundError, UniqueError

from app.models.company import Company as CompanyModel
from app.models.membership import Membership as MembershipModel, Member as MemberModel
from app.models.user import User as UserModel

from app.schemas.user import User
from app.schemas.membership import (Membership, MembershipTypes, MembershipCreate, MembershipParams,
                                    Member, MemberUpdate, CompanyMember, MemberCompany, MemberRoles)


class MembershipRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create_membership(self, payload: MembershipCreate) -> Membership:
        try:
            is_member = await self.is_member(company_id=payload.company_id, user_id=payload.user_id)
            if is_member:
                raise UniqueError('Member')
            is_owner = await self.is_owner(company_id=payload.company_id)
            is_acceptable = (payload.membership_type == MembershipTypes.invite
                             and is_owner
                             and self.current_user.id != payload.user_id
                             or
                             payload.membership_type == MembershipTypes.request
                             and not is_owner
                             and self.current_user.id == payload.user_id)
            if not is_acceptable:
                raise NotAuthorizedError(f'You can send an invitation to your company to any new user except yourself. '
                                         f'As well as send a request to join any new company other than your own.')
            query = insert(MembershipModel).values(
                user_id=payload.user_id,
                company_id=payload.company_id,
                membership_type=payload.membership_type,
            ).returning(MembershipModel)
            membership: Record = await self.db.fetch_one(query=query)
            return Membership(**membership)
        except UniqueViolationError:
            raise UniqueError(obj_name='Membership')
        except (ForeignKeyViolationError, AttributeError):
            raise NotFoundError(obj_name='Membership')

    async def get_memberships_all(self) -> list[Membership]:
        query = select(MembershipModel).order_by(desc(MembershipModel.membership_id))
        memberships_data: list[Record] = await self.db.fetch_all(query=query)
        return [Membership(**data) for data in memberships_data]

    async def get_memberships(self, q: MembershipParams) -> list[Membership]:
        q_data: dict = q.dict(exclude_unset=True, exclude_none=True)
        query = ''

        # All memberships
        if not q_data and self.current_user.is_superuser:
            query = select(MembershipModel).order_by(desc(MembershipModel.membership_id))

        if not q_data and not self.current_user.is_superuser:
            raise NotAuthorizedError

        # Company invites
        if (q.membership_type == MembershipTypes.invite and q.company_id
                and await self.is_owner(company_id=q.company_id)):
            query = select(MembershipModel).filter(
                MembershipModel.membership_type == MembershipTypes.invite,
                MembershipModel.company_id == q.company_id,
            ).order_by(desc(MembershipModel.membership_id))

        # Company requests
        if (q.membership_type == MembershipTypes.request and q.company_id
                and await self.is_owner(company_id=q.company_id)):
            query = select(MembershipModel).filter(
                MembershipModel.membership_type == MembershipTypes.request,
                MembershipModel.company_id == q.company_id,
            ).order_by(desc(MembershipModel.membership_id))

        # User invites
        if q.membership_type == MembershipTypes.invite and not q.company_id:
            query = select(MembershipModel).filter(
                MembershipModel.membership_type == MembershipTypes.invite,
                MembershipModel.user_id == self.current_user.id
            ).order_by(desc(MembershipModel.membership_id))

        # User requests
        if q.membership_type == MembershipTypes.request and not q.company_id:
            query = select(MembershipModel).filter(
                MembershipModel.user_id == self.current_user.id,
                MembershipModel.membership_type == MembershipTypes.request
            ).order_by(desc(MembershipModel.membership_id))

        memberships_data: list[Record] = await self.db.fetch_all(query=query)
        return [Membership(**data) for data in memberships_data]

    async def delete_membership(self, id: int) -> Membership:
        try:
            query = select(MembershipModel).filter(MembershipModel.membership_id == id).options(
                joinedload(MembershipModel.company))
            membership: Record = await self.db.fetch_one(query=query)
            if self.current_user.id not in (membership.user_id, membership.owner_id):
                raise NotAuthorizedError
            query = delete(MembershipModel).filter(MembershipModel.membership_id == id).returning(MembershipModel)
            membership: Record = await self.db.fetch_one(query=query)
            return Membership(**membership)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Membership')

    async def create_member(self, payload: Optional[Membership]) -> Member:
        try:
            query = select(MembershipModel).filter(
                MembershipModel.membership_id == payload.membership_id).options(
                joinedload(MembershipModel.company))
            membership: Record = await self.db.fetch_one(query=query)
            is_acceptable = (payload.membership_type == MembershipTypes.invite
                             and self.current_user.id != membership.owner_id
                             and self.current_user.id == payload.user_id
                             or
                             payload.membership_type == MembershipTypes.request
                             and self.current_user.id == membership.owner_id
                             and self.current_user.id != payload.user_id)
            if not is_acceptable:
                raise NotAuthorizedError(f'You can accept an invitation from any company other than your own. '
                                         f'As well as accept a request to your company from any user except yourself')
            query = insert(MemberModel).values(
                user_id=payload.user_id,
                company_id=payload.company_id,
                role=MemberRoles.member,
            ).returning(MemberModel)
            member: Record = await self.db.fetch_one(query=query)

            query = delete(MembershipModel).filter(
                MembershipModel.user_id == payload.user_id,
                MembershipModel.company_id == payload.company_id)
            await self.db.execute(query=query)
            return Member(**member)
        except UniqueViolationError:
            query = delete(MembershipModel).filter(MembershipModel.membership_id == payload.membership_id)
            await self.db.execute(query=query)
            raise UniqueError(obj_name='Member')
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Membership')

    async def get_company_members(self, company_id: int) -> list[CompanyMember]:
        query = select(MemberModel).filter(MemberModel.company_id == company_id).options(
            joinedload(MemberModel.member).load_only(UserModel.email)
        ).order_by(desc(MemberModel.m_id))
        members_data: list[Record] = await self.db.fetch_all(query=query)
        return [CompanyMember(**data) for data in members_data]

    async def get_member_companies(self, user_id: int) -> list[MemberCompany]:
        query = select(MemberModel).filter(MemberModel.user_id == user_id).options(
            joinedload(MemberModel.company).load_only(CompanyModel.comp_name)
        ).order_by(desc(MemberModel.m_id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        return [MemberCompany(**data) for data in companies_data]

    async def update_member(self, payload: MemberUpdate) -> Member:
        try:
            if self.current_user.id == payload.user_id:
                raise NotAuthorizedError(f'You are the owner of the Company ({payload.company_id}) '
                                         f'until the end of time')
            query = update(MemberModel).filter(
                MemberModel.company_id == payload.company_id,
                MemberModel.user_id == payload.user_id
            ).values(role=payload.role).returning(MemberModel)
            member: Record = await self.db.fetch_one(query=query)
            return Member(**member)
        except TypeError:
            raise NotFoundError(obj_name='Member')

    async def delete_member(self, id: int) -> Member:
        try:
            query = select(MemberModel).filter(MemberModel.m_id == id).options(
                joinedload(MemberModel.company))
            member: Record = await self.db.fetch_one(query=query)
            if self.current_user.id not in (member.user_id, member.owner_id):
                raise NotAuthorizedError
            query = delete(MemberModel).filter(MemberModel.m_id == id).returning(MemberModel)
            member: Record = await self.db.fetch_one(query=query)
            return Member(**member)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Member')

    async def is_member(self, company_id: Optional[int] = None, user_id: Optional[int] = None) -> bool:
        try:
            user_id = user_id or self.current_user.id
            query = select(MemberModel).filter(
                MemberModel.company_id == company_id,
                MemberModel.user_id == user_id)
            return await self.db.execute(query=query)
        except TypeError:
            return False

    async def is_admin(self, company_id: Optional[int] = None, user_id: Optional[int] = None) -> bool:
        try:
            user_id = user_id or self.current_user.id
            query = select(MemberModel).filter(
                MemberModel.company_id == company_id,
                MemberModel.user_id == user_id,
                or_(
                    MemberModel.role == MemberRoles.admin,
                    MemberModel.role == MemberRoles.owner,
                ))
            return await self.db.execute(query=query)
        except TypeError:
            return False

    async def is_owner(self, company_id: Optional[int] = None, user_id: Optional[int] = None) -> bool:
        try:
            user_id = user_id or self.current_user.id
            query = select(MemberModel).filter(
                MemberModel.company_id == company_id,
                MemberModel.user_id == user_id,
                MemberModel.role == MemberRoles.owner)
            return await self.db.execute(query=query)
        except (TypeError, AttributeError):
            return False
