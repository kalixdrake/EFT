from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from orders.models import Cart
from products.models import Category, Product


PASSWORD = 'StrongPass123!'


def create_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class CartAPITests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='cart@example.com', email='cart@example.com', password=PASSWORD)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {create_jwt_for_user(self.user)}')
        self.category = Category.objects.create(name='Shoes', slug='shoes')
        self.product = Product.objects.create(
            category=self.category,
            name='Runner',
            slug='runner',
            description='Runner shoe',
            price='100.00',
            cost_price='60.00',
            sku='SKU-RUN',
            stock=5,
        )

    def test_get_creates_empty_cart(self):
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 0)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_add_update_and_remove_cart_item(self):
        add_response = self.client.post('/api/cart/add/', {'product_id': self.product.pk, 'quantity': 2}, format='json')
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(add_response.data['items'][0]['quantity'], 2)

        item_id = add_response.data['items'][0]['id']
        update_response = self.client.put(f'/api/cart/update/{item_id}/', {'quantity': 3}, format='json')
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['items'][0]['quantity'], 3)

        delete_response = self.client.delete(f'/api/cart/remove/{item_id}/')
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.data['items'], [])

    def test_add_cart_item_rejects_stock_overflow(self):
        response = self.client.post('/api/cart/add/', {'product_id': self.product.pk, 'quantity': 99}, format='json')
        self.assertEqual(response.status_code, 400)