from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException, status
from sqlalchemy import desc, insert, select
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError

from app.models.company import memberships, Membership as MembershipModel, Company as CompanyModel
from app.schemas.membership import Membership, MembershipTypes, MembershipApplication, MembershipQuery
from app.schemas.company import Company
from app.schemas.user import User


class MembershipRepository:
    def __init__(self, db: Database):
        self.db = db

    async def get_current_company(self, payload: Membership | MembershipApplication) -> Company:
        comp_id = payload.company_id
        if comp_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not validate Company id"
            )
        query = select(CompanyModel).where(CompanyModel.comp_id == comp_id)
        company_data: Record = await self.db.fetch_one(query=query)
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={comp_id} does not exist in the system"
            )
        return Company(**company_data)

    async def create(self, payload: MembershipApplication, current_user: User) -> Membership:
        current_company = await self.get_current_company(payload=payload)
        is_owner = (payload.membership_type == MembershipTypes.invite and payload.user_id == current_user.id or
                    payload.membership_type == MembershipTypes.request and payload.user_id == current_company.owner_id)
        if is_owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with these credentials is the owner of the company"
            )
        query = insert(MembershipModel).values(
            user_id=payload.user_id,
            company_id=payload.company_id,
            membership_type=payload.membership_type,
        ).returning(MembershipModel)
        try:
            membership_dict: Record = await self.db.fetch_one(query=query)
            return Membership(**membership_dict)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Membership with this credentials already exist"
            )
        except ForeignKeyViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User or Company with this credentials does not exist"
            )

    async def get_all(self) -> list[Membership]:
        query = memberships.select().order_by(desc(memberships.c.membership_id))
        memberships_data: list[Record] = await self.db.fetch_all(query=query)
        if memberships_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There are no memberships in the system"
            )
        return [Membership(**data) for data in memberships_data]

    async def filter(self, q: MembershipQuery, current_user: User) -> list[Membership]:
        q_data: dict = q.dict(exclude_unset=True, exclude_none=True)
        query = ''

        if not q_data and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The user doesn't have enough privileges"
            )

        # all memberships
        if not q_data and current_user.is_superuser:
            query = select(MembershipModel).order_by(desc(MembershipModel.membership_id))

        # Current company invites
        if q.membership_type == MembershipTypes.invite and q.company_id:
            current_company = await self.get_current_company(payload=q)
            query = select(MembershipModel).filter(
                MembershipModel.membership_type == MembershipTypes.invite,
                MembershipModel.company_id == current_company.comp_id,
            ).order_by(desc(memberships.c.membership_id))

        # Current company requests
        if q.membership_type == MembershipTypes.request and q.company_id:
            current_company = await self.get_current_company(payload=q)
            query = select(MembershipModel).filter(
                MembershipModel.membership_type == MembershipTypes.request,
                MembershipModel.company_id == current_company.comp_id,
            ).order_by(desc(memberships.c.membership_id))

        # Current user invites
        if q.membership_type == MembershipTypes.invite and not q.company_id:
            query = select(MembershipModel).filter(
                MembershipModel.user_id == current_user.id,
                MembershipModel.membership_type == MembershipTypes.invite,
            ).order_by(desc(memberships.c.membership_id))

        # Current user requests
        if q.membership_type == MembershipTypes.request and not q.company_id:
            query = select(MembershipModel).filter(
                MembershipModel.user_id == current_user.id,
                MembershipModel.membership_type == MembershipTypes.request
            ).order_by(desc(memberships.c.membership_id))

        memberships_data: list[Record] = await self.db.fetch_all(query=query)
        if memberships_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There are no memberships in the system"
            )
        return [Membership(**data) for data in memberships_data]
