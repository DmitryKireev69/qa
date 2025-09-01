from django.db import models
from django.db.models import QuerySet
import uuid


class Question(models.Model):
    text: models.TextField = models.TextField(verbose_name="Текст вопроса")
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"Вопрос #{self.id}"

    @classmethod
    def get_all_questions(cls) -> QuerySet['Question']:
        """Получить все вопросы"""
        return cls.objects.all()


class Answer(models.Model):
    question: models.ForeignKey = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Вопрос"
    )
    user_id: models.UUIDField = models.UUIDField(default=uuid.uuid4, verbose_name="ID пользователя")
    text: models.TextField = models.TextField(verbose_name="Текст ответа")
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name: str = "Ответ"
        verbose_name_plural: str = "Ответы"
        ordering: list[str] = ['-created_at']
        indexes: list[models.Index] = [
            models.Index(fields=['user_id']),
            models.Index(fields=['question']),
        ]

    def __str__(self) -> str:
        return f"Ответ #{self.id} на вопрос #{self.question.id}"

    @classmethod
    def get_answers_for_question(cls, question_id: int) -> QuerySet['Answer']:
        """Получить ответы для конкретного вопроса"""
        return cls.objects.filter(question_id=question_id)