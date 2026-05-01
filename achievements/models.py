from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class Achievement(TimeStampedModel):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    points = models.PositiveIntegerField(default=100, verbose_name="Очки за достижение")
    icon = models.CharField(max_length=50, default='🏅', verbose_name="Иконка")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

class UserAchievement(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements', verbose_name="Пользователь")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name="Достижение")
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения")

    def __str__(self):
        return f"{self.user.username} — {self.achievement.title}"

    class Meta:
        unique_together = ('user', 'achievement')
        verbose_name = "Полученное достижение"
        verbose_name_plural = "Полученные достижения"