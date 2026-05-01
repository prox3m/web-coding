import sys
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from game.models import GameSession
from leaderboard.models import LeaderboardEntry


class APIAccessAndCRUDTest(APITestCase):
    def setUp(self):
        self.guest_client = APIClient()
        self.user = User.objects.create_user(username='api_user', password='apipass')
        self.token = Token.objects.create(user=self.user)
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.admin = User.objects.create_superuser(username='admin_api', password='adminpass', email='adm@api.com')

    def test_guest_can_view_public_endpoints(self):
        self.assertEqual(self.guest_client.get(reverse('leaderboard-list')).status_code, 200)
        self.assertEqual(self.guest_client.get(reverse('shopitem-list')).status_code, 200)

    def test_guest_cannot_access_protected(self):
        self.assertIn(self.guest_client.get(reverse('profile')).status_code, [401, 403])
        self.assertIn(self.guest_client.post(reverse('gamesession-list'), {}).status_code, [401, 403])

    def test_user_crud_game_session(self):
        res = self.auth_client.post(reverse('gamesession-list'), {
            'game_state': {'x': 10}, 'score': 500, 'level': 2, 'time_played': 60, 'is_completed': False
        }, format='json')
        self.assertEqual(res.status_code, 201)
        session_id = res.data['id']

        res = self.auth_client.get(reverse('gamesession-detail', args=[session_id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['score'], 500)

        res = self.auth_client.patch(reverse('gamesession-detail', args=[session_id]), {'score': 550})
        self.assertEqual(res.status_code, 200)

        res = self.auth_client.delete(reverse('gamesession-detail', args=[session_id]))
        self.assertEqual(res.status_code, 204)
        self.assertEqual(GameSession.objects.count(), 0)

    def test_latest_save_endpoint(self):
        GameSession.objects.create(user=self.user, score=100, level=1, time_played=10)
        GameSession.objects.create(user=self.user, score=200, level=2, time_played=20)
        res = self.auth_client.get(reverse('gamesession-latest'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['score'], 200)

    @unittest.skipIf(sys.version_info >= (3, 14), "Django admin rendering fails on Python 3.14+ due to copy issue")
    def test_admin_access(self):
        client = Client()
        client.force_login(self.admin)
        response = client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)