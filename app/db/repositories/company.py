from typing import Optional
from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException, status
from sqlalchemy import desc, insert, select
from sqlalchemy.orm import joinedload

from app.models.company import companies
from app.models.company import Company as CompanyModel
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.user import User


class CompanyRepository:
    def __init__(self, db: Database):
        self.db = db

    async def create(self, payload: CompanyCreate, current_user: User) -> Company:
        query = insert(CompanyModel).values(
            comp_name=payload.comp_name,
            comp_description=payload.comp_description,
            is_private=payload.is_private,
            owner_id=current_user.id,
        ).returning(CompanyModel)
        try:
            company: Record = await self.db.fetch_one(query=query)
            return Company(**company)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with id={id} already exist"
            )

    async def get(self, id: int, current_user: User) -> Company:
        query = select(CompanyModel).where(CompanyModel.comp_id == id)
        company: Record = await self.db.fetch_one(query=query)
        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        if company.is_private and company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Company with id={id} is private"
            )
        return Company(**company)

    async def get_all(self, current_user: User) -> list[Company]:
        query = companies.select().order_by(desc(companies.c.comp_id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        companies_list = [Company(**data) for data in companies_data]
        return [company for company in companies_list
                if not (company.is_private and company.owner_id != current_user.id)]

    async def delete(self, id: int, current_user: User) -> Company:
        query = select(CompanyModel).where(CompanyModel.comp_id == id)
        company: Record = await self.db.fetch_one(query=query)
        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        if company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not the owner of the Company id={id}")
        query = companies.delete().where(companies.c.comp_id == id).returning(*companies.c)
        company: Record = await self.db.fetch_one(query=query)
        return Company(**company)

    async def update(self, id: int, payload: CompanyUpdate, current_user: User) -> Optional[Company]:
        update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            return
        query = companies.select().where(companies.c.comp_id == id)
        company_data: Record = await self.db.fetch_one(query=query)
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        if company_data.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not the owner of the Company id={id}"
            )
        query = companies.update().where(companies.c.comp_id == id).values(**update_data).returning(*companies.c)
        company_dict: Record = await self.db.fetch_one(query=query)
        return Company(**company_dict)

    async def get_with_owner(self, id: int):
        query = select(CompanyModel).where(CompanyModel.comp_id == id
                                           ).options(joinedload(CompanyModel.owner))
        company_data: Record = await self.db.fetch_one(query=query)
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        return Company(**company_data, owner=User(**company_data))

    async def get_my(self, current_user: User) -> list[Company]:
        query = select(CompanyModel).where(CompanyModel.owner_id == current_user.id
                                           ).order_by(desc(CompanyModel.comp_id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        return [Company(**data) for data in companies_data]

