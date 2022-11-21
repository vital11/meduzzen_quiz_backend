from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user
from app.db.repositories.company import CompanyRepository
from app.schemas.company import Company, CompanyUpdate, CompanyCreate
from app.schemas.user import User


router = APIRouter(tags=["companies"])


@router.post("/companies/", response_model=Company)
async def create_company(payload: CompanyCreate, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.create(payload=payload, current_user=current_user)


@router.get("/companies/{id}", response_model=Company)
async def read_company(id: int, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.get(id=id)


@router.get("/companies", response_model=list[Company])
async def read_companies(current_user: User = Depends(get_current_user)) -> list[Company]:
    company_repo = CompanyRepository(db=database)
    return await company_repo.get_all()


@router.delete("/companies/{id}", response_model=Company)
async def delete_company(id: int, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.delete(id=id, current_user=current_user)


@router.patch("/companies/{id}", response_model=Company)
async def update_company(id: int, payload: CompanyUpdate, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.update(id=id, payload=payload, current_user=current_user)


# Temp
@router.post("/companies/orm/", response_model=Company)
async def create_company_orm(payload: CompanyCreate, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.create_orm(payload=payload, current_user=current_user)


@router.get("/companies/orm/{id}", response_model=Company)
async def read_company_orm(id: int, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database)
    return await company_repo.get_orm(id=id)
