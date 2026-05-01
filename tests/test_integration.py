from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from game.models import GameSession
from leaderboard.models import LeaderboardEntry
from shop.models import ShopItem, Purchase

class FullCycleIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_complete_user_flow(self):
        res = self.client.post('/api/users/register/', {
            'username': 'flow_user', 'email': 'flow@test.com', 'password': 'FlowPass123!', 'password2': 'FlowPass123!'
        })
        self.assertEqual(res.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {res.data['token']}")
        user = User.objects.get(username='flow_user')

        # ✅ FIX: format='json'
        res = self.client.post('/api/game/sessions/', {
            'game_state': {'progress': 0.5}, 'score': 1200, 'level': 3, 'time_played': 240, 'is_completed': False
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(GameSession.objects.filter(user=user).count(), 1)

        res = self.client.post('/api/leaderboard/', {
            'player_name': 'flow_user', 'score': 1200, 'difficulty': 'medium'
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(LeaderboardEntry.objects.filter(user=user).count(), 1)

        item = ShopItem.objects.create(name='Laser Paddle', price=200, is_active=True)
        res = self.client.post('/api/shop/purchases/', {'item_id': item.id}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Purchase.objects.filter(user=user).count(), 1)

        self.assertEqual(user.game_sessions.count(), 1)
        self.assertEqual(user.leaderboard_entries.count(), 1)
        self.assertEqual(user.purchases.count(), 1)