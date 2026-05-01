from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, UserAchievementViewSet

router = DefaultRouter()
router.register(r'list', AchievementViewSet, basename='achievement')
router.register(r'my', UserAchievementViewSet, basename='userachievement')

urlpatterns = [path('', include(router.urls))]