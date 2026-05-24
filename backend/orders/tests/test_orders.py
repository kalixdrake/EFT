from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from orders.models import Cart, CartItem, Order, OrderItem
from products.models import Category, Product


PASSWORD = 'StrongPass123!'


def create_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class OrderAPITests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='buyer@example.com', email='buyer@example.com', password=PASSWORD)
        self.other = get_user_model().objects.create_user(username='other@example.com', email='other@example.com', password=PASSWORD)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {create_jwt_for_user(self.user)}')
        self.category = Category.objects.create(name='Accessories', slug='accessories')
        self.product = Product.objects.create(
            category=self.category,
            name='Cap',
            slug='cap',
            description='Baseball cap',
            price='40.00',
            cost_price='15.00',
            sku='SKU-CAP',
            stock=4,
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_create_order_from_cart(self):
        response = self.client.post('/api/orders/create/', {
            'shipping_address': 'Street 123',
            'shipping_city': 'Medellin',
            'shipping_department': 'Antioquia',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total'], '80.00')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_list_orders_only_returns_owner_orders(self):
        Order.objects.create(user=self.other, status='pending', total='10.00', shipping_address='x', shipping_city='Bogota', shipping_department='Cundinamarca')
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_order_detail_returns_items(self):
        order = Order.objects.create(user=self.user, status='pending', total='80.00', shipping_address='Street 123', shipping_city='Medellin', shipping_department='Antioquia')
        OrderItem.objects.create(order=order, product=self.product, product_name=self.product.name, price=self.product.price, quantity=2)
        response = self.client.get(f'/api/orders/{order.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['product_name'], 'Cap')