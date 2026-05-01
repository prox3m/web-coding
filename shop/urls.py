from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.CoffeeProductViewSet, basename='product')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view({'post': 'create'})),
    path('auth/login/', views.CustomTokenObtainPairView.as_view()),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view()),
    path('', include(router.urls)),
]