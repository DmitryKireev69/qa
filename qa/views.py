from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from typing import Any, Dict
import logging

from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer, AnswerCreateSerializer
from .schemas import QuestionResponse, AnswerResponse

logger = logging.getLogger(__name__)


class QuestionListCreateView(generics.ListCreateAPIView):
    queryset: QuerySet[Question] = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(f"Создание нового вопроса: {request.data}")

        # Валидация через Pydantic
        try:
            from .schemas import QuestionCreate
            QuestionCreate(**request.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().list(request, *args, **kwargs)
        # Преобразуем в Pydantic схему для валидации вывода
        questions = [QuestionResponse(**item) for item in response.data['results']]
        response.data['results'] = [question.model_dump() for question in questions]
        return response


class QuestionDetailView(generics.RetrieveDestroyAPIView):
    queryset: QuerySet[Question] = Question.objects.all()
    serializer_class = QuestionSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(f"Получение вопроса с ID: {kwargs['pk']}")
        response = super().retrieve(request, *args, **kwargs)
        # Валидация вывода через Pydantic
        question = QuestionResponse(**response.data)
        return Response(question.model_dump())

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: Question = self.get_object()
        logger.info(f"Удаление вопроса с ID: {instance.id}")
        return super().destroy(request, *args, **kwargs)


class AnswerCreateView(generics.CreateAPIView):
    queryset: QuerySet[Answer] = Answer.objects.all()
    serializer_class = AnswerCreateSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        question_id: int = kwargs.get('question_id')
        question: Question = get_object_or_404(Question, id=question_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Добавляем вопрос к валидированным данным
        validated_data: Dict[str, Any] = serializer.validated_data
        validated_data['question'] = question

        # Создаем ответ
        answer: Answer = serializer.save()

        logger.info(
            f"Создан ответ с ID: {answer.id} для вопроса с ID: {question_id}, user_id: {answer.user_id}")

        # Возвращаем ответ в формате Pydantic
        answer_data = AnswerResponse.from_orm(answer).model_dump()
        return Response(answer_data, status=status.HTTP_201_CREATED)


class AnswerDetailView(generics.RetrieveDestroyAPIView):
    queryset: QuerySet[Answer] = Answer.objects.all()
    serializer_class = AnswerSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(f"Получение ответа с ID: {kwargs['pk']}")
        response = super().retrieve(request, *args, **kwargs)
        # Валидация вывода через Pydantic
        answer = AnswerResponse(**response.data)
        return Response(answer.model_dump())

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: Answer = self.get_object()
        logger.info(f"Удаление ответа с ID: {instance.id}")
        return super().destroy(request, *args, **kwargs)