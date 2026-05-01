from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CoffeeProduct, User

class APIBaseTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass123')
        self.product = CoffeeProduct.objects.create(
            name='Ethiopia Yirgacheffe',
            price=1200.00,
            origin='Ethiopia',
            roast_level='light',
            weight_g=250,
            stock=50
        )

    def authenticate(self, user=None):
        u = user or self.user
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': u.username, 'password': 'adminpass123' if u == self.admin else 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

class TestAuthAndPermissions(APIBaseTest):
    def test_register_and_login(self):
        res = self.client.post('/api/auth/register/', {'username': 'new', 'password': 'newpass123'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.authenticate()
        self.assertIsNotNone(self.token)

    def test_unauthenticated_access_denied(self):
        res = self.client.get('/api/products/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class TestProductsAndPagination(APIBaseTest):
    def test_list_products_with_pagination(self):
        self.authenticate()
        res = self.client.get('/api/products/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('count', res.data)
        self.assertIn('results', res.data)
        self.assertEqual(res.data['results'][0]['name'], self.product.name)

    def test_search_and_ordering(self):
        self.authenticate()
        res = self.client.get('/api/products/?search=Ethiopia&ordering=price')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data['results']), 0)

    def test_create_product_requires_auth(self):
        self.authenticate()
        # По умолчанию IsAuthenticated. Для продакшена можно добавить IsAdminUser
        res = self.client.post('/api/products/', {
            'name': 'Colombia Supremo', 'price': 900, 'origin': 'Colombia',
            'roast_level': 'medium', 'weight_g': 500, 'stock': 100
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)