from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from locations.models import Address, Department, Municipality
from orders.models import Order, OrderItem
from products.models import Category, Product
from shipping.models import Shipment, ShippingQuote
from shipping.services.skydropx import SkydropxClient, SkydropxError
from shipping.tasks import crear_guia_envio


class SkydropxIntegrationTests(TransactionTestCase):
    def setUp(self):
        if not settings.SKYDROPX_CLIENT_ID or not settings.SKYDROPX_CLIENT_SECRET:
            self.skipTest('SKYDROPX_CLIENT_ID / SKYDROPX_CLIENT_SECRET no están configuradas.')

        # Validate OAuth2 credentials by fetching a real token
        import requests as req
        try:
            r = req.post(
                f'{settings.SKYDROPX_API_BASE_URL}/oauth/token',
                json={
                    'client_id': settings.SKYDROPX_CLIENT_ID,
                    'client_secret': settings.SKYDROPX_CLIENT_SECRET,
                    'grant_type': 'client_credentials',
                },
                timeout=15,
            )
            if r.status_code >= 400:
                self.skipTest(f'Skydropx OAuth falló ({r.status_code}): {r.text[:200]}')
        except Exception as e:
            self.skipTest(f'No se pudo conectar a Skydropx: {e}')

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='StrongPass123!',
            phone='5544332211',
        )
        access_token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        self.category = Category.objects.create(name='Accessories', slug='accessories')
        self.product = Product.objects.create(
            category=self.category,
            name='Cap',
            slug='cap',
            description='Baseball cap',
            price='40000.00',
            cost_price='15000.00',
            box_length_cm='10.00',
            box_width_cm='10.00',
            box_height_cm='10.00',
            weight_kg='1.000',
            shipping_credit_cop='0.00',
            sku='SKU-CAP',
            stock=10,
        )
        department = Department.objects.create(name='Jalisco')
        municipality = Municipality.objects.create(department=department, name='Guadalajara')
        self.address = Address.objects.create(
            user=self.user,
            municipality=municipality,
            line='Av. Principal 123',
            postal_code='44100',
            is_default=True,
            label='Entregar en portería',
        )

    def _origin_settings(self):
        return {
            'SKYDROPX_ORIGIN_POSTAL_CODE': '06600',
            'SHIPPING_ORIGIN_NAME': 'EFT Store',
            'SHIPPING_ORIGIN_ADDRESS': 'Insurgentes Sur 1234',
            'SHIPPING_ORIGIN_CITY': 'Cuauhtemoc',
            'SHIPPING_ORIGIN_STATE': 'Ciudad de Mexico',
            'SHIPPING_ORIGIN_COUNTRY': 'MX',
            'SHIPPING_ORIGIN_PHONE': '5555555555',
            'SHIPPING_ORIGIN_EMAIL': 'logistica@eft.test',
            'SHIPPING_DESTINATION_COUNTRY': 'MX',
        }

    def test_oauth_token_fetched(self):
        """Client can obtain an OAuth2 Bearer token from the sandbox."""
        client = SkydropxClient()
        token = client._get_access_token()
        self.assertTrue(token)
        self.assertGreater(len(token), 20)

    def test_oauth_token_cached(self):
        """Second call returns cached token without hitting network again."""
        client = SkydropxClient()
        token1 = client._get_access_token()
        token2 = client._get_access_token()
        self.assertEqual(token1, token2)

    def test_shipping_quote_integration(self):
        """POST /api/shipping/quote/ returns valid quotes from Skydropx sandbox."""
        payload = {
            'cart_items': [{'product_id': self.product.id, 'quantity': 1}],
            'destination_city': 'Guadalajara',
            'destination_postal_code': '44100',
            'destination_area_level1': 'Jalisco',
        }
        with override_settings(**self._origin_settings()):
            response = self.client.post('/api/shipping/quote/', payload, format='json')

        if response.status_code == 404 and response.data.get('detail') == 'No hay cotizaciones disponibles.':
            self.skipTest('Skydropx sandbox sin cotizaciones para esta ruta.')

        self.assertEqual(response.status_code, 200, response.data)
        data = response.data
        self.assertIn('quotes', data)
        self.assertTrue(data['quotes'], 'Se esperaba al menos una cotización.')
        quote = data['quotes'][0]
        self.assertIn('quote_id', quote)
        self.assertIn('carrier', quote)
        self.assertIn('cost_after_credit', quote)
        # Quote persisted in DB
        self.assertTrue(
            ShippingQuote.objects.filter(user=self.user, destination_postal_code='44100').exists()
        )

    def test_quote_stores_quotation_and_rate_ids(self):
        """Stored ShippingQuote has skydropx_quotation_id and skydropx_rate_id for shipment creation."""
        payload = {
            'cart_items': [{'product_id': self.product.id, 'quantity': 1}],
            'destination_city': 'Guadalajara',
            'destination_postal_code': '44100',
            'destination_area_level1': 'Jalisco',
        }
        with override_settings(**self._origin_settings()):
            response = self.client.post('/api/shipping/quote/', payload, format='json')

        if response.status_code == 404:
            self.skipTest('Skydropx sandbox sin cotizaciones para esta ruta.')

        self.assertEqual(response.status_code, 200, response.data)
        quote_id = response.data['quotes'][0]['quote_id']
        quote_obj = ShippingQuote.objects.get(quote_id=quote_id)
        self.assertTrue(quote_obj.skydropx_quotation_id, 'skydropx_quotation_id debe estar guardado.')
        self.assertTrue(quote_obj.skydropx_rate_id, 'skydropx_rate_id debe estar guardado.')

    def test_crear_guia_envio_integration(self):
        """crear_guia_envio task creates a real Skydropx shipment and stores tracking data."""
        payload = {
            'cart_items': [{'product_id': self.product.id, 'quantity': 1}],
            'destination_city': 'Guadalajara',
            'destination_postal_code': '44100',
            'destination_area_level1': 'Jalisco',
        }
        with override_settings(**self._origin_settings()):
            response = self.client.post('/api/shipping/quote/', payload, format='json')

        if response.status_code == 404:
            self.skipTest('Skydropx sandbox sin cotizaciones para esta ruta.')

        self.assertEqual(response.status_code, 200, response.data)
        quote_id = response.data['quotes'][0]['quote_id']
        quote = ShippingQuote.objects.get(quote_id=quote_id)

        if not quote.skydropx_quotation_id or not quote.skydropx_rate_id:
            self.skipTest('Sandbox no devolvió quotation/rate IDs necesarios.')

        order = Order.objects.create(
            user=self.user,
            address=self.address,
            shipping_quote=quote,
            shipping_method=quote.carrier,
            payment_method=Order.PaymentMethod.BOLD,
            shipping_cost_before_credit=quote.cost_cop,
            shipping_credit_applied=Decimal('0.00'),
            shipping_cost=quote.cost_cop,
            total=self.product.price,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=1,
        )

        with override_settings(**self._origin_settings()):
            crear_guia_envio(order.id)

        order.refresh_from_db()
        shipment = Shipment.objects.get(order=order)
        self.assertEqual(order.status, Order.Status.SHIPPED)
        self.assertTrue(shipment.tracking_number, 'Debe tener tracking_number.')
        self.assertTrue(shipment.skydropx_shipment_id, 'Debe tener skydropx_shipment_id.')
