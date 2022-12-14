from typing import Optional
from pydantic import BaseModel, validator


class QuestionBase(BaseModel):
    question_name: Optional[str] = None
    answers: Optional[list[str]] = None
    right_answer: Optional[str] = None
    quiz_id: Optional[int] = None


# Properties to receive via API on creation
class QuestionCreate(QuestionBase):
    question_name: str
    # answers: list[str]
    # right_answer: str
    right_answers: Optional[list[str]]
    right_answer: Optional[str]


class QuestionUpdate(QuestionBase):
    question_name: Optional[str]
    # answers: Optional[list[str]]
    answers: Optional[str]
    right_answer: Optional[str]


class QuestionInDBBase(QuestionBase):
    question_id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Question(QuestionInDBBase):
    pass


class QuestionParams(Question):

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


# Shared properties
class QuizBase(BaseModel):
    quiz_name: Optional[str] = None
    quiz_description: Optional[str] = None
    company_id: Optional[int] = None
    questions: Optional[list[Question]] = None
    frequency: Optional[int] = 0


# Properties to receive via API on creation
class QuizCreate(QuizBase):
    quiz_name: str
    company_id: int


class QuizUpdate(BaseModel):
    quiz_name: Optional[str]
    quiz_description: Optional[str]
    questions: Optional[list[QuestionUpdate]]

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value


class QuizInDBBase(QuizBase):
    quiz_id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Quiz(QuizInDBBase):
    pass
