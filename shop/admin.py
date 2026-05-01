from django.contrib import admin
from .models import ShopItem, Purchase

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'price_paid', 'created_at')
    search_fields = ('user__username', 'item__name')
    ordering = ('-created_at',)