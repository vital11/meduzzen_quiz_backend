from typing import Optional

from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update, and_
from sqlalchemy.orm import joinedload

from app.core.exception import UniqueError, NotFoundError
from app.models.quiz import Quiz as QuizModel, Question as QuestionModel
from app.schemas.quiz import (Quiz, QuizCreate, Question, QuestionCreate, QuestionDelete,
                              DescriptionUpdate, QuestionsUpdate)
from app.schemas.user import User


class QuizRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create(self, payload: QuizCreate) -> Quiz:
        try:
            query = insert(QuizModel).values(
                quiz_name=payload.quiz_name,
                quiz_description=payload.quiz_description,
                company_id=payload.company_id,
            ).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            questions = await self._insert_questions(quiz_id=quiz.quiz_id, payload=payload.questions)
            return Quiz(**quiz, questions=questions)
        except UniqueViolationError:
            raise UniqueError(obj_name='Quiz')
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def get(self, quiz_id: int) -> Quiz:
        try:
            query = select(QuizModel).filter(QuizModel.quiz_id == quiz_id).options(
                joinedload(QuizModel.questions))
            quizzes: list[Record] = await self.db.fetch_all(query=query)
            quiz = quizzes[-1]
            questions = [Question(**quiz) for quiz in quizzes]
            return Quiz(**quiz, questions=questions)
        except (TypeError, AttributeError, IndexError):
            raise NotFoundError(obj_name='Quiz')

    async def get_company_quizzes(self, company_id: int) -> list[Quiz]:
        query = select(QuizModel).filter(
            QuizModel.company_id == company_id
        ).order_by(desc(QuizModel.quiz_id))
        quizzes: list[Record] = await self.db.fetch_all(query=query)
        return [Quiz(**quiz) for quiz in quizzes]

    async def update_quiz_description(self, payload: DescriptionUpdate) -> Quiz:
        try:
            update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
            query = update(QuizModel).filter(QuizModel.quiz_id == payload.quiz_id).values(
                **update_data
            ).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            query = select(QuestionModel).filter(QuestionModel.quiz_id == payload.quiz_id)
            questions_data: list[Record] = await self.db.fetch_all(query=query)
            questions = [Question(**data) for data in questions_data]
            return Quiz(**quiz, questions=questions)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def update_quiz_questions(self, payload: QuestionsUpdate) -> Quiz:
        try:
            await self._delete_questions(quiz_id=payload.quiz_id, payload=payload.questions)
            await self._insert_questions(quiz_id=payload.quiz_id, payload=payload.questions)
            return await self.get(quiz_id=payload.quiz_id)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def _insert_questions(self, quiz_id: int, payload: list[QuestionCreate]) -> list[Question]:
        try:
            query = insert(QuestionModel).values(
                [{**dict(p), 'quiz_id': quiz_id} for p in payload]
            ).returning(QuestionModel)
            questions: list[Record] = await self.db.fetch_all(query=query)
            return [Question(**question) for question in questions]
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def _delete_questions(self, quiz_id: int, payload: Optional[list[QuestionDelete] | list[QuestionsUpdate]]) -> None:
        try:
            question_names = [question.question_name for question in payload]
            query = delete(QuestionModel).filter(
                and_(
                    QuestionModel.quiz_id == quiz_id,
                    QuestionModel.question_name.in_(question_names)
                ))
            await self.db.execute(query=query)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def delete(self, quiz_id: int) -> Quiz:
        try:
            query = delete(QuizModel).filter(QuizModel.quiz_id == quiz_id).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            return Quiz(**quiz)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')
