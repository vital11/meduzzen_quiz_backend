from typing import Optional
from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update

from app.core.exception import UniqueError, NotFoundError, NotAuthorizedError
from app.models.company import Company as CompanyModel
from app.models.membership import Member as MemberModel
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.membership import MemberRoles
from app.schemas.user import User


class CompanyRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create(self, payload: CompanyCreate) -> Company:
        try:
            query = insert(CompanyModel).values(
                comp_name=payload.comp_name,
                comp_description=payload.comp_description,
                is_private=payload.is_private,
                owner_id=self.current_user.id,
            ).returning(CompanyModel)
            company: Record = await self.db.fetch_one(query=query)
            query = insert(MemberModel).values(
                user_id=self.current_user.id,
                company_id=company.comp_id,
                role=MemberRoles.owner,
            )
            await self.db.execute(query=query)
            return Company(**company)
        except UniqueViolationError:
            raise UniqueError(obj_name='Company')

    async def get(self, id: int) -> Company:
        try:
            query = select(CompanyModel).filter(CompanyModel.comp_id == id)
            company: Record = await self.db.fetch_one(query=query)
            is_member = await self.is_member(company_id=id)
            if company.is_private and not is_member:
                raise NotAuthorizedError(f'Company with id={id} is private')
            return Company(**company)
        except TypeError:
            raise NotFoundError(obj_name='Company')

    async def get_all(self) -> list[Company]:
        query = select(CompanyModel).order_by(desc(CompanyModel.comp_id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        companies_list = [Company(**data) for data in companies_data]
        return [company for company in companies_list
                if not (company.is_private and company.owner_id != self.current_user.id)]

    async def get_by_owner(self, user_id: Optional[int]) -> list[Company]:
        user_id = user_id or self.current_user.id
        query = select(CompanyModel).filter(CompanyModel.owner_id == user_id).order_by(desc(CompanyModel.comp_id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        return [Company(**data) for data in companies_data]

    async def update(self, id: int, payload: CompanyUpdate) -> Company:
        try:
            update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
            query = update(CompanyModel).filter(
                CompanyModel.comp_id == id).values(**update_data).returning(CompanyModel)
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Company')

    async def delete(self, id: int) -> Company:
        try:
            query = delete(CompanyModel).filter(CompanyModel.comp_id == id).returning(CompanyModel)
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Company')

    async def is_member(self, company_id: Optional[int] = None, user_id: Optional[int] = None) -> bool:
        try:
            user_id = user_id or self.current_user.id
            query = select(MemberModel).filter(
                MemberModel.company_id == company_id,
                MemberModel.user_id == user_id)
            return await self.db.execute(query=query)
        except TypeError:
            return False
