from django.test import TestCase
from django.urls import reverse
from .models import StudentGrade
from .forms import StudentForm

class DatabaseTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'full_name': 'Иванов Иван', 'group_number': '101', 'subject': 'Математика',
            'grade': 4, 'date': '15-05-2024', 'storage_type': 'database', 'save_data': '1'
        }

    def test_duplicate_prevention(self):
        StudentGrade.objects.create(full_name='Иванов Иван', group_number='101', subject='Математика', grade=4, date='15-05-2024')
        response = self.client.post(reverse('home'), self.valid_data, follow=True)
        self.assertContains(response, "Такая запись уже есть")
        self.assertEqual(StudentGrade.objects.count(), 1)

    def test_ajax_search(self):
        StudentGrade.objects.create(full_name='Петров Пётр', group_number='202', subject='Физика', grade=5, date='10-06-2024')
        response = self.client.get(reverse('ajax_search'), {'q': 'Петров'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.json()['count'], 1)