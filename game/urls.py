from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSessionViewSet

router = DefaultRouter()
router.register(r'sessions', GameSessionViewSet, basename='gamesession')

urlpatterns = [path('', include(router.urls))]