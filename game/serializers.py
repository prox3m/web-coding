from rest_framework import serializers
from .models import GameSession

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['id', 'game_state', 'score', 'level', 'time_played', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']