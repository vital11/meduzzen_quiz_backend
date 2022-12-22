from typing import Optional
from pydantic import BaseModel, conlist, validator, constr


class QuestionBase(BaseModel):
    quiz_id: Optional[int] = None
    question_name: Optional[str] = None
    answers: Optional[list[str]] = None
    right_answer: Optional[str] = None


# Properties to receive via API on creation
class QuestionCreate(QuestionBase):
    question_name: str
    answers: conlist(item_type=str, min_items=2, max_items=10, unique_items=True)
    right_answer: str


class QuestionUpdate(QuestionCreate):
    answers: conlist(item_type=str, max_items=10, unique_items=True)


class QuestionDelete(QuestionUpdate):
    question_name: str


class QuestionsUpdate(QuestionCreate):
    quiz_id: int
    company_id: int
    questions: Optional[list[QuestionUpdate]] | Optional[list[QuestionDelete]]


class QuestionInDBBase(QuestionBase):

    class Config:
        orm_mode = True


# Additional properties to return via API
class Question(QuestionInDBBase):
    pass


# Shared properties
class QuizBase(BaseModel):
    quiz_name: Optional[str] = None
    quiz_description: Optional[str] = None
    company_id: Optional[int] = None
    questions: Optional[list[Question]] = None
    frequency: Optional[int] = 0


# Properties to receive via API on creation
class QuizCreate(QuizBase):
    quiz_name: constr(min_length=1, strip_whitespace=True)
    quiz_description: Optional[str]
    questions: conlist(item_type=QuestionCreate, min_items=2)
    company_id: int


class QuizUpdate(QuizBase):
    quiz_id: Optional[int]
    quiz_name: Optional[str]
    quiz_description: Optional[str]
    questions: Optional[conlist(item_type=QuestionUpdate, min_items=2)]

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


class DescriptionUpdate(QuizBase):
    quiz_id: int

    @validator('*')
    def empty_str_to_none(cls, value):
        return None if value == '' else value
