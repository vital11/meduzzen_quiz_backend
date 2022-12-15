from fastapi import APIRouter, Depends

from app.db.database import database
from app.db.dependencies import get_current_user
from app.db.repositories.quiz import QuizRepository
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, Question
from app.schemas.user import User


router = APIRouter(tags=['quizzes'])


@router.post('/companies/{id}/quizzes/', response_model=Quiz)
async def create_quiz(
        id: int, payload: QuizCreate, current_user: User = Depends(get_current_user)) -> Quiz:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.create(company_id=id, payload=payload)


@router.get('/companies/quizzes/{id}', response_model=Quiz)
async def read_quiz(
        id: int, current_user: User = Depends(get_current_user)) -> Quiz:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.get(quiz_id=id)


@router.get('/companies/{id}/quizzes', response_model=list[Quiz])
async def read_company_quizzes(
        id: int, current_user: User = Depends(get_current_user)) -> list[Quiz]:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.get_company_quizzes(company_id=id)


@router.patch('/companies/{company_id}/quizzes/{quiz_id}', response_model=Quiz)
async def update_quiz_name(
        company_id: int, quiz_id: int, payload: QuizUpdate,
        current_user: User = Depends(get_current_user)) -> Quiz:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.update(company_id=company_id, quiz_id=quiz_id, payload=payload)


@router.patch('/companies/{company_id}/quizzes/{quiz_id}/questions/', response_model=list[Question])
async def update_quiz_questions(
        company_id: int, quiz_id: int, payload: QuizUpdate,
        current_user: User = Depends(get_current_user)) -> list[Question]:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.update_questions(company_id=company_id, quiz_id=quiz_id, payload=payload)


@router.delete('/companies/{company_id}/quizzes/{quiz_id}', response_model=Quiz)
async def delete_quiz(
        company_id: int, quiz_id: int, current_user: User = Depends(get_current_user)) -> Quiz:
    quiz_repo = QuizRepository(db=database, current_user=current_user)
    return await quiz_repo.delete(company_id=company_id, quiz_id=quiz_id)
