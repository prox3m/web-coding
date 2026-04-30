from django import forms

class EventForm(forms.Form):
    title = forms.CharField(max_length=100, label='Название')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Дата')
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label='Время')
    description = forms.CharField(widget=forms.Textarea, label='Описание', required=False)
    reminder = forms.IntegerField(min_value=0, max_value=120, label='Напомнить за (мин)', initial=15)

class SettingsForm(forms.Form):
    THEME_CHOICES = [('light', 'Светлая'), ('dark', 'Тёмная')]
    theme = forms.ChoiceField(choices=THEME_CHOICES, label='Тема', required=False)
    reminder_time = forms.IntegerField(min_value=0, max_value=120, label='Время напоминания по умолчанию (мин)', required=False)