from sqlalchemy import Column, Integer, ForeignKey, String, ARRAY, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

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

    question_name = Column(String(200))
    answers = Column(ARRAY(String))
    right_answer = Column(String(200))

    quiz_id = Column(Integer, ForeignKey('quizzes.quiz_id', ondelete='CASCADE', onupdate='CASCADE'))
    quiz = relationship('Quiz', back_populates='questions', cascade='save-update')

    __table_args__ = (
        UniqueConstraint('question_name', 'quiz_id', name='uniq_con'),
        PrimaryKeyConstraint('question_name', 'quiz_id', name='pk_con'),
    )
