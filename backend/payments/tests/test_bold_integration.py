import hashlib
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from locations.models import Address, Department, Municipality
from orders.models import Order
from payments.models import Payment


class BoldWebhookIntegrationTests(TransactionTestCase):
    def setUp(self):
        if not settings.BOLD_INTEGRITY_SECRET:
            self.skipTest('BOLD_INTEGRITY_SECRET no está configurada.')

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='StrongPass123!',
        )
        department = Department.objects.create(name='Antioquia')
        municipality = Municipality.objects.create(department=department, name='Medellin')
        self.address = Address.objects.create(
            user=self.user,
            municipality=municipality,
            line='Street 123',
            postal_code='050001',
            is_default=True,
        )
        self.order = Order.objects.create(user=self.user, address=self.address, total='100.00')

    def _signature(self, payload):
        body = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(body + settings.BOLD_INTEGRITY_SECRET.encode('utf-8')).hexdigest()

    def test_webhook_approves_payment_with_env_secret(self):
        payload = {
            'event': 'SALE_APPROVED',
            'transaction_id': 'txn_sandbox_123',
            'order_reference': self.order.order_number,
            'amount': 10000,
            'currency': 'COP',
            'timestamp': '2026-05-24T14:30:00Z',
        }
        # Serialize with the same format that will be sent as the request body
        body_bytes = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        signature = hashlib.sha256(body_bytes + settings.BOLD_INTEGRITY_SECRET.encode('utf-8')).hexdigest()
        response = self.client.post(
            '/api/payments/webhook/',
            body_bytes,
            content_type='application/json',
            HTTP_X_BOLD_SIGNATURE=signature,
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.status, Payment.Status.APPROVED)
