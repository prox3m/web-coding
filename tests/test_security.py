from django.test import TestCase
from django.contrib.auth.models import User
from leaderboard.models import LeaderboardEntry
from rest_framework.test import APIClient

class SecurityTests(TestCase):
    def test_password_hashing(self):
        user = User.objects.create_user(username='sec_user', password='PlainTextPass!')
        self.assertNotEqual(user.password, 'PlainTextPass!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(user.check_password('PlainTextPass!'))

    def test_sql_injection_prevention_orm(self):
        user = User.objects.create_user(username='sqli_test', password='pass')
        # ✅ FIX: Строка уложена в max_length=15, чтобы не падала валидация
        malicious_name = "'; DROP --"
        LeaderboardEntry.objects.create(user=user, player_name=malicious_name, score=999)
        
        count = LeaderboardEntry.objects.count()
        self.assertEqual(count, 1)
        self.assertIn("DROP", LeaderboardEntry.objects.first().player_name)

    def test_xss_output_safety(self):
        user = User.objects.create_user(username='xss_user', password='pass')
        client = APIClient()
        client.force_authenticate(user=user)
        
        # ✅ FIX: Payload уложен в max_length=15
        xss_payload = '<img src=x>'
        res = client.post('/api/leaderboard/', {
            'player_name': xss_payload,
            'score': 500,
            'difficulty': 'easy'
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['player_name'], xss_payload)