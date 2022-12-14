from asyncpg import UniqueViolationError
from databases import Database
from databases.backends.postgres import Record
from sqlalchemy import desc, insert, select, delete, update
from sqlalchemy.orm import joinedload

from app.core.exception import UniqueError, NotFoundError, NotAuthorizedError
from app.models.company import Company as CompanyModel
from app.models.quiz import Quiz as QuizModel, Question as QuestionModel
from app.schemas.membership import MemberList
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate
from app.schemas.user import User


class QuizRepository:
    def __init__(self, db: Database, current_user: User = None):
        self.db = db
        self.current_user = current_user

    async def create(self, company_id: int, payload: QuizCreate) -> Quiz:
        try:
            company_members = await self._get_company_members(company_id)
            if self.current_user.id not in company_members.admins:
                raise NotAuthorizedError
            query = insert(QuizModel).values(
                quiz_name=payload.quiz_name,
                company_id=company_id,
            ).returning(QuizModel)
            quiz: Record = await self.db.fetch_one(query=query)
            return Quiz(**quiz)
        except UniqueViolationError:
            raise UniqueError(obj_name='Quiz')
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def get(self, quiz_id: int) -> Quiz:
        try:
            query = select(QuizModel).filter(QuizModel.quiz_id == quiz_id)
            quiz: Record = await self.db.fetch_one(query=query)
            company_members = await self._get_company_members(quiz.company_id)
            if self.current_user.id not in company_members.members:
                raise NotAuthorizedError
            return Quiz(**quiz)
        except (TypeError, AttributeError):
            raise NotFoundError(obj_name='Quiz')

    async def get_company_quizzes(self, company_id: int) -> list[Quiz]:
        company_members = await self._get_company_members(company_id)
        query = select(QuizModel).filter(QuizModel.company_id == company_id).order_by(desc(QuizModel.quiz_id))
        quizzes: list[Record] = await self.db.fetch_all(query=query)
        return [Quiz(**quiz) for quiz in quizzes if self.current_user.id in company_members.members]

    async def update(self, company_id: int, quiz_id: int, payload: QuizUpdate) -> Quiz:
        pass

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
