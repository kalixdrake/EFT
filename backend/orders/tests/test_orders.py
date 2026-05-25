from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from locations.models import Address, Department, Municipality
from orders.models import Cart, CartItem, Order, OrderItem
from payments.models import Payment
from shipping.models import ShippingQuote
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
        department = Department.objects.create(name='Antioquia')
        municipality = Municipality.objects.create(department=department, name='Medellin')
        self.address = Address.objects.create(
            user=self.user,
            municipality=municipality,
            line='Street 123',
            postal_code='050001',
            is_default=True,
        )
        other_department = Department.objects.create(name='Cundinamarca')
        other_municipality = Municipality.objects.create(department=other_department, name='Bogota')
        self.other_address = Address.objects.create(
            user=self.other,
            municipality=other_municipality,
            line='Other street',
            postal_code='110111',
        )
        self.quote = ShippingQuote.objects.create(
            user=self.user,
            carrier='DHL',
            service='Ground',
            service_code='GROUND',
            estimated_days=3,
            cost_cop='20.00',
            destination_city='Medellin',
            destination_postal_code='050001',
        )

    def test_create_order_from_cart(self):
        response = self.client.post(
            '/api/orders/create/',
            {
                'address_id': self.address.pk,
                'shipping_quote_id': str(self.quote.quote_id),
                'payment_method': 'bold',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total'], '100.00')
        self.assertRegex(response.data['order_number'], r'^\d{8}-\d+$')
        self.assertEqual(response.data['address']['line'], 'Street 123')
        self.assertEqual(response.data['bold_data']['currency'], 'COP')
        self.assertEqual(response.data['bold_data']['amount_cents'], 10000)
        self.assertRegex(response.data['bold_data']['order_reference'], r'^\d{8}-\d+-[0-9a-f]{8}$')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        payment = Payment.objects.get(order_id=response.data['id'])
        self.assertEqual(payment.bold_reference, response.data['bold_data']['order_reference'])
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_create_order_rejects_foreign_address(self):
        response = self.client.post(
            '/api/orders/create/',
            {
                'address_id': self.other_address.pk,
                'shipping_quote_id': str(self.quote.quote_id),
                'payment_method': 'bold',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_list_orders_only_returns_owner_orders(self):
        Order.objects.create(user=self.other, address=self.other_address, status='pending', total='10.00')
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_order_detail_returns_items(self):
        order = Order.objects.create(user=self.user, address=self.address, status='pending', total='80.00')
        OrderItem.objects.create(order=order, product=self.product, product_name=self.product.name, price=self.product.price, quantity=2)
        response = self.client.get(f'/api/orders/{order.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['product_name'], 'Cap')
        self.assertEqual(response.data['order_number'], order.order_number)

    def test_retry_payment_returns_fresh_bold_data_for_pending_bold_orders(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            status=Order.Status.PENDING,
            payment_method=Order.PaymentMethod.BOLD,
            total='80.00',
        )
        payment = Payment.objects.create(
            order=order,
            amount='80.00',
            currency='COP',
            status=Payment.Status.REJECTED,
            transaction_id='txn_old',
            bold_reference=f'{order.order_number}-oldref00',
            metadata={'old': True},
        )

        response = self.client.post(f'/api/orders/{order.pk}/retry-payment/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['bold_data']['amount_cents'], 8000)
        self.assertNotEqual(response.data['bold_data']['order_reference'], payment.bold_reference)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertIsNone(payment.transaction_id)
        self.assertEqual(payment.metadata, {})
        self.assertEqual(payment.bold_reference, response.data['bold_data']['order_reference'])

    def test_retry_payment_rejects_non_pending_orders(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            status=Order.Status.CONFIRMED,
            payment_method=Order.PaymentMethod.BOLD,
            total='80.00',
        )
        Payment.objects.create(order=order, amount='80.00', currency='COP', status=Payment.Status.APPROVED)

        response = self.client.post(f'/api/orders/{order.pk}/retry-payment/')

        self.assertEqual(response.status_code, 400)
