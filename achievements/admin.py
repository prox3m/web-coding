from django.contrib import admin
from .models import Achievement, UserAchievement

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'points', 'icon', 'created_at')
    search_fields = ('title',)
    list_filter = ('points',)

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    search_fields = ('user__username', 'achievement__title')
    date_hierarchy = 'unlocked_at'
    ordering = ('-unlocked_at',)