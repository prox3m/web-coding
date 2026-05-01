from rest_framework import serializers
from .models import Achievement, UserAchievement

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'points', 'icon']

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'unlocked_at']