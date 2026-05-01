from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from users.models import UserProfile
from game.models import GameSession
from leaderboard.models import LeaderboardEntry
from achievements.models import Achievement, UserAchievement
from shop.models import ShopItem, Purchase

class TimeStampedModelTest(TestCase):
    def test_auto_fields_populated(self):
        user = User.objects.create_user(username='ts_test', password='pass')
        profile = UserProfile.objects.create(user=user)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        
        old_updated = profile.updated_at
        import time; time.sleep(0.02)
        profile.bio = 'Updated bio'
        profile.save()
        profile.refresh_from_db()
        self.assertGreater(profile.updated_at, old_updated)

class RelationsAndConstraintsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rel_user', password='pass')
        # ✅ FIX: Явно создаем профиль, так как create_user этого не делает
        UserProfile.objects.get_or_create(user=self.user)

    def test_user_profile_relation(self):
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user.username, 'rel_user')
        self.assertTrue(hasattr(profile, 'created_at'))

    def test_game_session_json(self):
        session = GameSession.objects.create(
            user=self.user,
            game_state={"level": 3, "paddle_x": 0.5, "balls": []},
            score=1500, level=3, time_played=300
        )
        self.assertEqual(session.game_state["level"], 3)
        self.assertIsInstance(session.game_state, dict)

    def test_leaderboard_choices_validation(self):
        entry = LeaderboardEntry(
            user=self.user, player_name='ValidName', score=500, difficulty='invalid_choice'
        )
        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_user_achievement_unique_constraint(self):
        ach = Achievement.objects.create(title='First Win', points=100)
        UserAchievement.objects.create(user=self.user, achievement=ach)
        with self.assertRaises(Exception):
            UserAchievement.objects.create(user=self.user, achievement=ach)

    def test_purchase_relation(self):
        item = ShopItem.objects.create(name='Shield', price=50, is_active=True)
        purchase = Purchase.objects.create(user=self.user, item=item, price_paid=50)
        self.assertEqual(purchase.item.name, 'Shield')
        self.assertEqual(self.user.purchases.count(), 1)