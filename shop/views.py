from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import CoffeeProduct, Cart, CartItem, Order, OrderItem
from .serializers import (
    UserRegistrationSerializer, CoffeeProductSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer
)

User = get_user_model()

# AUTH
class RegisterView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Автоматическое создание корзины при регистрации
        Cart.objects.create(user=user)
        return Response({"detail": "User created successfully. Please login."}, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    pass

class CustomTokenRefreshView(TokenRefreshView):
    pass

# CRUD
class CoffeeProductViewSet(viewsets.ModelViewSet):
    queryset = CoffeeProduct.objects.all()
    serializer_class = CoffeeProductSerializer
    search_fields = ['name', 'description', 'origin']
    ordering_fields = ['price', 'created_at', 'weight_g']
    filterset_fields = ['roast_level', 'origin', 'price']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()] # Админ/модератор права можно расширить через IsAdminUser

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # У пользователя только 1 корзина
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)
        total = 0
        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            total += item.product.price * item.quantity
            # Уменьшаем сток
            item.product.stock -= item.quantity
            item.product.save()
        
        order.total_price = total
        order.save()
        cart.items.all().delete() # Очищаем корзину после оформления
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)