from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from products.models import Category, Product


PASSWORD = 'StrongPass123!'


def create_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class ProductAPITests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Tshirts', slug='tshirts')
        self.active_product = Product.objects.create(
            category=self.category,
            name='Basic Tee',
            slug='basic-tee',
            description='A tee',
            price='50.00',
            cost_price='20.00',
            sku='SKU-001',
            stock=10,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name='Hidden Tee',
            slug='hidden-tee',
            description='Hidden',
            price='70.00',
            cost_price='30.00',
            sku='SKU-002',
            stock=0,
            is_active=False,
        )
        self.user = get_user_model().objects.create_user(username='client@example.com', email='client@example.com', password=PASSWORD)
        self.staff = get_user_model().objects.create_user(username='employee@example.com', email='employee@example.com', password=PASSWORD, role='employee')

    def test_public_list_filters_active_and_supports_search(self):
        response = self.client.get('/api/products/?search=basic')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Basic Tee')
        self.assertNotIn('cost_price', response.data[0])

    def test_staff_sees_cost_price_and_real_stock(self):
        token = create_jwt_for_user(self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['cost_price'], '20.00')
        self.assertEqual(response.data[0]['stock'], 10)

    def test_detail_returns_category_payload(self):
        response = self.client.get(f'/api/products/{self.active_product.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category']['slug'], 'tshirts')
        self.assertIn('images', response.data)
        self.assertIsInstance(response.data['images'], list)

    def test_categories_list(self):
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['slug'], 'tshirts')