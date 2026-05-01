from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
import datetime
from .models import GameSession

@admin.action(description='📥 Экспорт выбранных сессий в XLSX')
def export_to_xlsx(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Game Sessions"

    # 📌 Здесь можно менять поля для экспорта (требование: "возможность выбора полей")
    headers = ['ID', 'Игрок', 'Очки', 'Уровень', 'Время (сек)', 'Завершена', 'Дата создания']
    ws.append(headers)

    for session in queryset:
        ws.append([
            session.id,
            session.user.username,
            session.score,
            session.level,
            session.time_played,
            'Да' if session.is_completed else 'Нет',
            session.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=arkanoid_sessions_{datetime.date.today()}.xlsx'
    wb.save(response)
    return response

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'score', 'level', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'level', 'created_at')
    search_fields = ('user__username',)
    actions = [export_to_xlsx]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)