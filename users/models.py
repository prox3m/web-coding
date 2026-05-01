from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    bio = models.TextField(max_length=500, blank=True, default='', verbose_name="О себе")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"