import os
import tempfile
import json
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from . import utils
from .forms import StudentForm

class GradeAppTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = os.path.join(self.temp_dir.name, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    @override_settings(DATA_DIR=None)
    def test_form_validation(self):
        valid_data = {'full_name': 'Иванов Иван', 'group_number': '101', 'subject': 'Математика', 'grade': 4, 'date': '15-05-2024', 'export_format': 'json'}
        form = StudentForm(data=valid_data)
        self.assertTrue(form.is_valid())

        invalid_grade = valid_data.copy()
        invalid_grade['grade'] = 6
        self.assertFalse(StudentForm(data=invalid_grade).is_valid())

        invalid_date = valid_data.copy()
        invalid_date['date'] = '2024-05-15'
        self.assertFalse(StudentForm(data=invalid_date).is_valid())

    def test_filename_sanitization(self):
        self.assertEqual(utils.sanitize_text("Test@# Name!"), "Test_Name")
        self.assertEqual(utils.sanitize_text("   "), "data")

    @override_settings(DATA_DIR=lambda s: self.data_dir)
    def test_file_save_and_load(self):
        # Создаем временный файл для теста utils
        test_json = os.path.join(self.data_dir, 'test.json')
        with open(test_json, 'w') as f:
            json.dump({'full_name': 'Test', 'group_number': 'G1', 'subject': 'Sub', 'grade': 3, 'date': '01-01-2024'}, f)
        
        data, err = utils.validate_and_parse_json(test_json)
        self.assertIsNone(err)
        self.assertEqual(data['grade'], 3)
        os.remove(test_json)

    def test_upload_invalid_file(self):
        with override_settings(DATA_DIR=self.data_dir):
            invalid_xml = b"<invalid><root></root></invalid>"
            uploaded = SimpleUploadedFile("bad.xml", invalid_xml, content_type="text/xml")
            response = self.client.post(reverse('home'), {'upload_file': '1', 'file': uploaded}, follow=True)
            self.assertContains(response, "Файл невалиден")
            self.assertEqual(len(os.listdir(self.data_dir)), 0)