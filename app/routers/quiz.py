from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_admin_user, get_current_member_user
from app.db.repositories.quiz import QuizRepository
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, QuizDescription
from app.schemas.user import User


router = APIRouter(tags=['quizzes'])


@router.post('/quizzes/', response_model=Quiz)
async def create_quiz(
        payload: QuizCreate,
        current_user: User = Depends(get_current_admin_user)
) -> Quiz:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.create(payload=payload)


@router.get('/quizzes/companies/{company_id}', response_model=list[Quiz])
async def read_company_quizzes(
        company_id: int, current_user: User = Depends(get_current_member_user)
) -> list[Quiz]:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.get_company_quizzes(company_id=company_id)


@router.get('/quizzes/{company_id}/{quiz_id}',
            dependencies=[Depends(get_current_member_user)],
            response_model=Quiz)
async def read_quiz(quiz_id: int) -> Quiz:
    quiz_repo = QuizRepository(db=database)
    return await quiz_repo.get(quiz_id=quiz_id)


@router.patch('/quizzes/',
              dependencies=[Depends(get_current_admin_user)],
              response_model=Quiz)
async def update_quiz_description(payload: QuizDescription) -> Quiz:
    quiz_repo = QuizRepository(db=database)
    return await quiz_repo.update_quiz_description(payload=payload)


@router.patch('/quizzes/questions',
              dependencies=[Depends(get_current_admin_user)],
              response_model=Quiz)
async def update_quiz(payload: QuizUpdate) -> Quiz:
    quiz_repo = QuizRepository(db=database)
    return await quiz_repo.update_quiz(payload=payload)


@router.delete('/quizzes/{company_id}/{quiz_id}',
               dependencies=[Depends(get_current_admin_user)],
               response_model=Quiz)
async def delete_quiz(quiz_id: int) -> Quiz:
    quiz_repo = QuizRepository(db=database)
    return await quiz_repo.delete(quiz_id=quiz_id)
