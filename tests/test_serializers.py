from django.test import TestCase
from django.contrib.auth.models import User
from users.serializers import UserRegistrationSerializer
from game.serializers import GameSessionSerializer
from rest_framework.test import APIRequestFactory

class SerializerValidationTest(TestCase):
    def test_valid_registration(self):
        data = {
            'username': 'new_player',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'new_player')

    def test_invalid_password_mismatch(self):
        data = {
            'username': 'bad_player',
            'email': 'bad@example.com',
            'password': 'pass1',
            'password2': 'pass2'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)

    def test_game_session_serializer_context(self):
        user = User.objects.create_user(username='ctx_user', password='pass')
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = user
        data = {'game_state': {'lvl': 1}, 'score': 100, 'level': 1, 'time_played': 10, 'is_completed': False}
        serializer = GameSessionSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        # ✅ FIX: Явно передаем user, чтобы избежать null constraint
        session = serializer.save(user=user)
        self.assertEqual(session.user, user)