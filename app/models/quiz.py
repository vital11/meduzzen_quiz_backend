from sqlalchemy import Column, Integer, ForeignKey, String, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

from app.db.database import Base


class Quiz(Base):
    __tablename__ = 'quizzes'

    quiz_id = Column(Integer, primary_key=True, index=True)
    quiz_name = Column(String(50), index=True)
    quiz_description = Column(String(500))
    frequency = Column(Integer, default=0)

    company_id = Column(Integer, ForeignKey('companies.comp_id', ondelete='CASCADE', onupdate='CASCADE'))
    company = relationship('Company', back_populates='quizzes')

    questions = relationship('Question', back_populates='quiz', cascade='all, delete')


class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True, index=True)
    question_name = Column(String(200))
    # answers = Column(MutableList.as_mutable(ARRAY(String)))
    answers = Column(String(200))
    right_answer = Column(String(200))

    quiz_id = Column(Integer, ForeignKey('quizzes.quiz_id', ondelete='CASCADE', onupdate='CASCADE'))
    quiz = relationship('Quiz', back_populates='questions', cascade='save-update')
