from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class LeaderboardEntry(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leaderboard_entries', verbose_name="Игрок")
    player_name = models.CharField(max_length=15, verbose_name="Имя игрока")
    score = models.PositiveIntegerField(verbose_name="Очки")
    rank = models.PositiveIntegerField(default=0, verbose_name="Ранг")
    difficulty = models.CharField(
        max_length=10,
        choices=[('easy', 'Лёгкий'), ('medium', 'Средний'), ('hard', 'Сложный')],
        default='medium',
        verbose_name="Сложность"
    )
    date_achieved = models.DateTimeField(auto_now_add=True, verbose_name="Дата достижения")

    def __str__(self):
        return f"{self.player_name} — {self.score} очков ({self.difficulty})"

    class Meta:
        ordering = ['-score']
        verbose_name = "Запись в таблице лидеров"
        verbose_name_plural = "Таблица лидеров"