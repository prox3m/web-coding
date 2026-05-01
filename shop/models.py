from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class ShopItem(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Название предмета")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.PositiveIntegerField(verbose_name="Цена (в игровой валюте)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    icon = models.CharField(max_length=50, default='🎁', verbose_name="Иконка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар в магазине"
        verbose_name_plural = "Товары в магазине"

class Purchase(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases', verbose_name="Покупатель")
    item = models.ForeignKey(ShopItem, on_delete=models.PROTECT, verbose_name="Предмет")
    price_paid = models.PositiveIntegerField(verbose_name="Цена покупки")

    def __str__(self):
        return f"{self.user.username} купил {self.item.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"