from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import ShopItem, Purchase
from .serializers import ShopItemSerializer, PurchaseSerializer

class ShopItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShopItem.objects.filter(is_active=True)
    serializer_class = ShopItemSerializer
    permission_classes = [permissions.AllowAny]

class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user).select_related('item')

    def create(self, request, *args, **kwargs):
        item_id = request.data.get('item_id')
        try:
            item = ShopItem.objects.get(id=item_id, is_active=True)
        except ShopItem.DoesNotExist:
            return Response({'detail': 'Предмет не найден или недоступен'}, status=status.HTTP_404_NOT_FOUND)

        # Фиксируем покупку
        purchase = Purchase.objects.create(user=request.user, item=item, price_paid=item.price)
        return Response(self.get_serializer(purchase).data, status=status.HTTP_201_CREATED)