from django.contrib import admin
from .models import LeaderboardEntry

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'score', 'rank', 'difficulty', 'date_achieved')
    list_filter = ('difficulty', 'date_achieved')
    search_fields = ('player_name', 'user__username')
    ordering = ('-score',)