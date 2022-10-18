from typing import List
from fastapi import APIRouter

from app.models.company import companies
from app.schemas.company import Company, CompanyIn
from app.db.database import database


router = APIRouter()


@router.get("/companies/", response_model=List[Company])
async def get_companies():
    query = companies.select()
    return await database.fetch_all(query)


@router.post("/companies/", response_model=Company)
async def create_company(company: CompanyIn):
    query = companies.insert().values(title=company.title, description=company.description)
    last_record_id = await database.execute(query)
    return {**company.dict(), "id": last_record_id}


