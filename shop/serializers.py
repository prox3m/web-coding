from rest_framework import serializers
from .models import ShopItem, Purchase

class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = ['id', 'name', 'description', 'price', 'icon', 'is_active']

class PurchaseSerializer(serializers.ModelSerializer):
    item = ShopItemSerializer(read_only=True)
    class Meta:
        model = Purchase
        fields = ['id', 'item', 'price_paid', 'created_at']
        read_only_fields = ['id', 'created_at']