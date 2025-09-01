from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
import uuid


class AnswerBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Текст ответа")

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Текст ответа не может быть пустым")
        return v.strip()


class AnswerCreate(AnswerBase):
    user_id: Optional[uuid.UUID] = Field(None, description="ID пользователя (опционально)")


class AnswerResponse(AnswerBase):
    id: int
    question_id: int
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Текст вопроса")

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Текст вопроса не может быть пустым")
        return v.strip()


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True


class AnswerDetailResponse(AnswerResponse):
    question: QuestionResponse

    class Config:
        from_attributes = True