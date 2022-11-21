from typing import Optional
from databases import Database
from databases.backends.postgres import Record
from fastapi import HTTPException, status
from sqlalchemy import desc, insert, select, and_
from sqlalchemy.orm import joinedload, defaultload

from app.models.company import companies
from app.models.company import Company as CompanyModel
from app.models.user import User as UserModel, users
from app.schemas.company import CompanyCreate, Company, CompanyUpdate
from app.schemas.user import User


class CompanyRepository:
    def __init__(self, db: Database):
        self.db = db

    async def create(self, payload: CompanyCreate, current_user: User) -> Company:
        query = companies.insert().values(
            name=payload.name,
            description=payload.description,
            is_private=payload.is_private,
            owner_id=current_user.id,
        ).returning(*companies.c)
        company_dict: Record = await self.db.fetch_one(query=query)
        return Company(**company_dict)

    async def get(self, id: int) -> Optional[Company]:
        query = companies.select().where(companies.c.id == id)
        company_data: Record = await self.db.fetch_one(query=query)
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        return Company(**company_data)

    async def get_all(self) -> list[Company]:
        query = companies.select().order_by(desc(companies.c.id))
        companies_data: list[Record] = await self.db.fetch_all(query=query)
        return [Company(**data) for data in companies_data]

    async def delete(self, id: int, current_user: User) -> Company:
        query = companies.select().where(companies.c.id == id)
        company_data: Record = await self.db.fetch_one(query=query)
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        if company_data.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not the owner of the Company id={id}")
        query = companies.delete().where(companies.c.id == id).returning(*companies.c)
        company_data: Record = await self.db.fetch_one(query=query)
        return Company(**company_data)

    async def update(self, id: int, payload: CompanyUpdate, current_user: User) -> Optional[Company]:
        update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            return

        query = companies.select().where(companies.c.id == id)
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
        query = companies.update().where(companies.c.id == id).values(**update_data).returning(*companies.c)
        company_dict: Record = await self.db.fetch_one(query=query)
        return Company(**company_dict)

    # Temp ORM
    async def create_orm(self, payload: CompanyCreate, current_user: User) -> Company:
        query = insert(CompanyModel).values(
            name=payload.name,
            description=payload.description,
            is_private=payload.is_private,
            owner_id=current_user.id
        ).returning(CompanyModel)
        company_dict: Record = await self.db.fetch_one(query=query)
        return Company(**company_dict)

    async def get_orm(self, id: int) -> Optional[Company]:

        query = select(CompanyModel).where(CompanyModel.id == id).options(
            # joinedload(CompanyModel.owner)
            defaultload(CompanyModel.owner)
        )

        # query = select(CompanyModel).where(
        #     CompanyModel.id == id).join(UserModel)

        company_data: Record = await self.db.fetch_one(query=query)
        print('------------', Company(**company_data))
        if company_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id={id} does not exist in the system"
            )
        return Company(**company_data)







