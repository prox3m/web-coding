from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

class StudentGrade(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    group_number = models.CharField(max_length=20, verbose_name='Группа')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    grade = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])
    date = models.CharField(max_length=10, verbose_name='Дата (ДД-ММ-ГГГГ)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['full_name', 'subject', 'date']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} | {self.subject}"

    def clean(self):
        super().clean()
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', self.date):
            raise ValidationError({'date': 'Формат даты: ДД-ММ-ГГГГ'})