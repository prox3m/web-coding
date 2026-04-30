# grade_app/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

class StudentGrade(models.Model):
    """Модель для хранения успеваемости в SQLite"""
    full_name = models.CharField(max_length=100, verbose_name='ФИО студента')
    group_number = models.CharField(max_length=20, verbose_name='Номер группы')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    grade = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    date = models.CharField(max_length=10, verbose_name='Дата сдачи (ДД-ММ-ГГГГ)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Запись об успеваемости'
        verbose_name_plural = 'Записи об успеваемости'
        unique_together = ['full_name', 'subject', 'date']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} | {self.subject} | {self.grade}"

    def clean(self):
        """Валидация формата даты на уровне модели"""
        super().clean()
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', self.date):
            raise ValidationError({'date': 'Дата должна быть в формате ДД-ММ-ГГГГ.'})