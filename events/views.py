from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import EventForm, SettingsForm

# Данные в памяти (словари событий)
events_list = [
    {
        'id': 1,
        'title': 'Встреча с командой',
        'date': '2026-05-05',
        'time': '10:00',
        'description': 'Обсуждение спринта',
        'reminder': 15,
    },
    {
        'id': 2,
        'title': 'Сдать отчёт',
        'date': '2026-05-07',
        'time': '18:00',
        'description': 'Последний день',
        'reminder': 30,
    },
]

def index(request):
    # Читаем cookies
    theme = request.COOKIES.get('theme', 'light')
    default_reminder = int(request.COOKIES.get('reminder_time', 15))

    # Обработка формы события
    if request.method == 'POST' and 'add_event' in request.POST:
        form = EventForm(request.POST)
        if form.is_valid():
            new_id = max([e['id'] for e in events_list], default=0) + 1
            events_list.append({
                'id': new_id,
                'title': form.cleaned_data['title'],
                'date': form.cleaned_data['date'].strftime('%Y-%m-%d'),
                'time': form.cleaned_data['time'].strftime('%H:%M'),
                'description': form.cleaned_data['description'],
                'reminder': form.cleaned_data['reminder'],
            })
            # Перенаправление с GET-параметром статуса
            return redirect(f"{reverse('events:index')}?status=success")
        # Если форма не валидна, продолжит отображение с ошибками

    # Подготовка форм
    event_form = EventForm(initial={'reminder': default_reminder})
    settings_form = SettingsForm(initial={'theme': theme, 'reminder_time': default_reminder})

    context = {
        'events': events_list,
        'event_form': event_form,
        'settings_form': settings_form,
        'theme': theme,
    }
    return render(request, 'events/index.html', context)

def save_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            theme = form.cleaned_data['theme']
            reminder_time = form.cleaned_data['reminder_time']
            response = HttpResponseRedirect(reverse('events:index'))  # исправлено имя
            response.set_cookie('theme', theme, max_age=30*24*60*60)
            response.set_cookie('reminder_time', reminder_time, max_age=30*24*60*60)
            return response
    return redirect('events:index')