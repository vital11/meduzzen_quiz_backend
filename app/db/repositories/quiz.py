from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update, and_
from sqlalchemy.orm import joinedload

from app.core.exception import UniqueError, NotFoundError, NotAuthorizedError
from app.models.company import Company as CompanyModel
from app.models.quiz import Quiz as QuizModel, Question as QuestionModel
from app.schemas.membership import MemberList
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, Question, QuestionCreate, QuestionDelete
from app.schemas.user import User


class QuizRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create(self, company_id: int, payload: QuizCreate) -> Quiz:
        try:
            await self._is_admin(company_id)
            query = insert(QuizModel).values(
                quiz_name=payload.quiz_name,
                company_id=company_id,
            ).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            questions = await self._create_questions(quiz_id=quiz.quiz_id, payload=payload.questions)
            return Quiz(**quiz, questions=questions)
        except UniqueViolationError:
            raise UniqueError(obj_name='Quiz')
        except (TypeError, AttributeError) as e:
            print(e)
            raise NotFoundError(obj_name='Quiz')

    async def get(self, quiz_id: int) -> Quiz:
        try:
            query = select(QuizModel).filter(QuizModel.quiz_id == quiz_id).options(
                joinedload(QuizModel.questions))
            quizzes: list[Record] = await self.db.fetch_all(query=query)
            quiz = quizzes[-1]
            questions = [Question(**quiz) for quiz in quizzes]
            await self._is_member(quiz.company_id)
            return Quiz(**quiz, questions=questions)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def get_company_quizzes(self, company_id: int) -> list[Quiz]:
        await self._is_member(company_id)
        query = select(QuizModel).filter(
            QuizModel.company_id == company_id
        ).order_by(desc(QuizModel.quiz_id))
        quizzes: list[Record] = await self.db.fetch_all(query=query)
        return [Quiz(**quiz) for quiz in quizzes]

    async def update(self, company_id: int, quiz_id: int, payload: QuizUpdate) -> Quiz:
        try:
            await self._is_admin(company_id)
            update_data: dict = payload.dict(exclude_unset=True, exclude_none=True)
            query = update(QuizModel).filter(QuizModel.quiz_id == quiz_id).values(
                **update_data
            ).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            return Quiz(**quiz)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def update_questions(self, company_id: int, quiz_id: int, payload: QuizUpdate) -> list[Question]:
        try:
            await self._is_admin(company_id)
            await self._delete_questions(quiz_id=quiz_id, payload=payload.questions)
            return await self._create_questions(quiz_id=quiz_id, payload=payload.questions)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def delete(self, company_id: int, quiz_id: int) -> Quiz:
        try:
            company_members = await self._get_company_members(company_id)
            if self.current_user.id not in company_members.admins:
                raise NotAuthorizedError
            query = delete(QuizModel).filter(QuizModel.quiz_id == quiz_id).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            return Quiz(**quiz)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def _create_questions(self, quiz_id: int, payload: list[QuestionCreate]) -> list[Question]:
        try:
            query = insert(QuestionModel).values(
                [{**dict(p), 'quiz_id': quiz_id} for p in payload]
            ).returning(QuestionModel)
            questions: list[Record] = await self.db.fetch_all(query=query)
            return [Question(**question) for question in questions]
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def _delete_questions(self, quiz_id: int, payload: list[QuestionDelete]) -> None:
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

    async def _get_company_members(self, company_id: int) -> MemberList:
        try:
            query = select(CompanyModel).filter(CompanyModel.comp_id == company_id).options(
                joinedload(CompanyModel.members))
            members_data: list[Record] = await self.db.fetch_all(query=query)
            members = [d.user_id for d in members_data]
            admins = [d.user_id for d in members_data if d.is_admin]
            owner = members_data[-1].owner_id
            members.append(owner)
            admins.append(owner)
            return MemberList(members=members, admins=admins, owner=owner)
        except TypeError:
            raise NotFoundError(obj_name='Company')

    async def _is_admin(self, company_id: int) -> bool:
        company_members = await self._get_company_members(company_id)
        if self.current_user.id not in company_members.admins:
            raise NotAuthorizedError
        return True

    async def _is_member(self, company_id: int) -> bool:
        company_members = await self._get_company_members(company_id)
        if self.current_user.id not in company_members.admins:
            raise NotAuthorizedError
        return True
