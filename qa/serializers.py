from rest_framework import serializers
from django.db import models
from typing import Dict, Any, Optional
import uuid

from .models import Question, Answer
from .schemas import AnswerCreate, QuestionCreate


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields: list[str] = ['id', 'question', 'user_id', 'text', 'created_at']
        read_only_fields: list[str] = ['id', 'created_at', 'user_id']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields: list[str] = ['id', 'text', 'created_at', 'answers']
        read_only_fields: list[str] = ['id', 'created_at', 'answers']

    def validate_text(self, value: str) -> str:
        """Валидация текста вопроса"""
        if not value.strip():
            raise serializers.ValidationError("Текст вопроса не может быть пустым")
        return value


class AnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=False)

    class Meta:
        model = Answer
        fields: list[str] = ['user_id', 'text']
        read_only_fields: list[str] = ['id', 'created_at']

    def validate_user_id(self, value: Optional[str]) -> Optional[uuid.UUID]:
        """Валидация user_id"""
        if value:
            try:
                return uuid.UUID(str(value))
            except ValueError:
                raise serializers.ValidationError("Некорректный формат user_id")
        return None

    def validate_text(self, value: str) -> str:
        """Валидация текста ответа"""
        if not value.strip():
            raise serializers.ValidationError("Текст ответа не может быть пустым")
        return value

    def to_internal_value(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразование данных для Pydantic"""
        validated_data = super().to_internal_value(data)

        # Создаем Pydantic модель для дополнительной валидации
        try:
            answer_create = AnswerCreate(**validated_data)
            return answer_create.model_dump()
        except ValueError as e:
            raise serializers.ValidationError(str(e))