from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user
from app.db.repositories.company import CompanyRepository
from app.schemas.company import Company, CompanyUpdate, CompanyCreate
from app.schemas.user import User


router = APIRouter(tags=['companies'])


@router.post('/companies/', response_model=Company)
async def create_company(
        payload: CompanyCreate, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.create(payload=payload)


@router.get('/companies/{id}', response_model=Company)
async def read_company(id: int, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.get(id=id)


@router.get('/companies', response_model=list[Company])
async def read_companies(current_user: User = Depends(get_current_user)) -> list[Company]:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.get_all()


@router.get('/companies/owner/', response_model=list[Company])
async def read_owner_companies(
        id: int | None = None, current_user: User = Depends(get_current_user)) -> list[Company]:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.get_by_owner(user_id=id)


@router.patch('/companies/{id}', response_model=Company)
async def update_company(
        id: int, payload: CompanyUpdate, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.update(id=id, payload=payload)


@router.delete('/companies/{id}', response_model=Company)
async def delete_company(id: int, current_user: User = Depends(get_current_user)) -> Company:
    company_repo = CompanyRepository(db=database, current_user=current_user)
    return await company_repo.delete(id=id)
