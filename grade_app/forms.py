from django import forms
import re
from datetime import datetime

class StudentForm(forms.Form):
    full_name = forms.CharField(label='ФИО студента', max_length=100)
    group_number = forms.CharField(label='Номер группы', max_length=20)
    subject = forms.CharField(label='Предмет', max_length=100)
    grade = forms.IntegerField(label='Оценка', min_value=2, max_value=5)
    date = forms.CharField(label='Дата сдачи (ДД-ММ-ГГГГ)', max_length=10)
    export_format = forms.ChoiceField(
        label='Формат сохранения',
        choices=[('json', 'JSON'), ('xml', 'XML')],
        widget=forms.RadioSelect
    )

    def clean_full_name(self):
        name = self.cleaned_data['full_name']
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', name):
            raise forms.ValidationError("ФИО может содержать только буквы, пробелы и дефисы.")
        return name.strip()

    def clean_date(self):
        date_str = self.cleaned_data['date']
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
            raise forms.ValidationError("Формат даты должен быть строго ДД-ММ-ГГГГ.")
        try:
            datetime.strptime(date_str, '%d-%m-%Y')
        except ValueError:
            raise forms.ValidationError("Некорректная дата.")
        return date_str