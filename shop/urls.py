from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopItemViewSet, PurchaseViewSet

router = DefaultRouter()
router.register(r'items', ShopItemViewSet, basename='shopitem')
router.register(r'purchases', PurchaseViewSet, basename='purchase')

urlpatterns = [path('', include(router.urls))]