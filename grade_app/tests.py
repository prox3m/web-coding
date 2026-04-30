from django.test import TestCase
from django.urls import reverse
from .models import StudentGrade
from .forms import StudentForm

class DatabaseTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'full_name': 'Иванов Иван',
            'group_number': '101',
            'subject': 'Математика',
            'grade': 4,
            'date': '15-05-2024',
            'storage_type': 'database',
            'save_data': '1'  # 🔑 FIX: Имитируем нажатие кнопки "Сохранить"
        }

    def test_model_creation(self):
        data = {k: v for k, v in self.valid_data.items() if k not in ('storage_type', 'save_data')}
        StudentGrade.objects.create(**data)
        self.assertEqual(StudentGrade.objects.count(), 1)

    def test_duplicate_prevention(self):
        # Создаём первую запись
        data = {k: v for k, v in self.valid_data.items() if k not in ('storage_type', 'save_data')}
        StudentGrade.objects.create(**data)
        
        # Пытаемся сохранить дубликат через форму
        response = self.client.post(reverse('home'), self.valid_data, follow=True)
        self.assertContains(response, "Такая запись уже есть в базе данных")
        self.assertEqual(StudentGrade.objects.count(), 1)

    def test_form_validation_date_format(self):
        bad_data = self.valid_data.copy()
        bad_data['date'] = '2024-05-15'
        form = StudentForm(data=bad_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_ajax_search(self):
        StudentGrade.objects.create(
            full_name='Петров Пётр', group_number='202', 
            subject='Физика', grade=5, date='10-06-2024'
        )
        response = self.client.get(reverse('ajax_search'), {'q': 'Петров'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['subject'], 'Физика')