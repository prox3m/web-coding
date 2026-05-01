from rest_framework import serializers
from .models import LeaderboardEntry

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)

    class Meta:
        model = LeaderboardEntry
        fields = ['id', 'username', 'player_name', 'score', 'rank', 'difficulty', 'date_achieved']