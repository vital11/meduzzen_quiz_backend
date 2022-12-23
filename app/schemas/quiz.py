from typing import Optional
from pydantic import BaseModel, conlist, validator, constr


class QuestionBase(BaseModel):
    question_name: str
    answers: conlist(item_type=str, min_items=2, max_items=10, unique_items=True)
    right_answer: str


class QuestionInDBBase(QuestionBase):
    quiz_id: int

    class Config:
        orm_mode = True


class Question(QuestionInDBBase):
    pass


# Shared properties
class QuizBase(BaseModel):
    quiz_name: Optional[str] = None
    quiz_description: Optional[str] = None
    frequency: Optional[int] = 0
    company_id: int
    questions: Optional[list[Question]]


# Properties to receive via API on creation
class QuizCreate(QuizBase):
    quiz_name: constr(min_length=1, strip_whitespace=True)
    quiz_description: Optional[str]
    questions: conlist(item_type=QuestionBase, min_items=2)


class QuizUpdate(QuizBase):
    quiz_id: int
    questions: list[QuestionBase]


class QuizInDBBase(QuizBase):
    quiz_id: Optional[int] = None

    class Config:
        orm_mode = True


class Quiz(QuizInDBBase):
    pass


class QuizDescription(QuizBase):
    quiz_id: int

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value
