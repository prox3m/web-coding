from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class GameSession(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions', verbose_name="Игрок")
    game_state = models.JSONField(default=dict, verbose_name="Состояние игры (JSON)")
    score = models.PositiveIntegerField(default=0, verbose_name="Очки")
    level = models.PositiveIntegerField(default=1, verbose_name="Уровень")
    time_played = models.PositiveIntegerField(default=0, verbose_name="Время в игре (сек)")
    is_completed = models.BooleanField(default=False, verbose_name="Завершена")

    def __str__(self):
        return f"Сессия {self.user.username} | Очки: {self.score}"

    class Meta:
        ordering = ['-score']
        verbose_name = "Игровая сессия"
        verbose_name_plural = "Игровые сессии"