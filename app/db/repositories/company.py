from typing import Optional
from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update

from app.core.exception import UniqueError, NotFoundError, NotAuthorizedError
from app.models.company import Company as CompanyModel
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.user import User


class CompanyRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create(self, payload: CompanyCreate) -> Company:
        query = insert(CompanyModel).values(
            comp_name=payload.comp_name,
            comp_description=payload.comp_description,
            is_private=payload.is_private,
            owner_id=self.current_user.id,
        ).returning(CompanyModel)
        try:
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except UniqueViolationError:
            raise UniqueError(obj_name='Company')

    async def get(self, id: int) -> Company:
        try:
            company = await self._get_company(id=id)
            if company.is_private and company.owner_id != self.current_user.id:
                raise NotAuthorizedError(f'Company with id={id} is private')
            return company
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
            query = select(CompanyModel).filter(CompanyModel.comp_id == id)
            company: Record = await self.db.fetch_one(query=query)
            if company.owner_id != self.current_user.id:
                raise NotAuthorizedError(f'You are not the owner of the Company id={id}')
            query = update(CompanyModel).filter(
                CompanyModel.comp_id == id).values(**update_data).returning(CompanyModel)
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Company')

    async def delete(self, id: int) -> Company:
        try:
            query = select(CompanyModel).filter(CompanyModel.comp_id == id)
            company: Record = await self.db.fetch_one(query=query)
            if company.owner_id != self.current_user.id:
                raise NotAuthorizedError(f'You are not the owner of the Company id={id}')
            query = delete(CompanyModel).filter(CompanyModel.comp_id == id).returning(CompanyModel)
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Company')

    async def _get_company(self, id: int) -> Company:
        try:
            query = select(CompanyModel).filter(CompanyModel.comp_id == id)
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except TypeError:
            raise NotFoundError(obj_name='Company')
