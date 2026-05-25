import hashlib
import json

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from locations.models import Address, Department, Municipality
from orders.models import Order
from payments.models import Payment


PASSWORD = 'StrongPass123!'


@override_settings(BOLD_INTEGRITY_SECRET='secret-key')
class BoldWebhookTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password=PASSWORD,
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
        return hashlib.sha256(body + b'secret-key').hexdigest()

    def test_webhook_approves_payment(self):
        payload = {
            'event': 'SALE_APPROVED',
            'transaction_id': 'txn_abc123',
            'order_reference': self.order.order_number,
            'amount': 10000,
            'currency': 'COP',
            'timestamp': '2026-05-24T14:30:00Z',
        }
        response = self.client.post(
            '/api/payments/webhook/',
            payload,
            format='json',
            HTTP_X_BOLD_SIGNATURE=self._signature(payload),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.status, Payment.Status.APPROVED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def test_webhook_is_idempotent(self):
        payload = {
            'event': 'SALE_APPROVED',
            'transaction_id': 'txn_abc123',
            'order_reference': self.order.order_number,
            'amount': 10000,
            'currency': 'COP',
            'timestamp': '2026-05-24T14:30:00Z',
        }
        signature = self._signature(payload)
        self.client.post('/api/payments/webhook/', payload, format='json', HTTP_X_BOLD_SIGNATURE=signature)
        response = self.client.post('/api/payments/webhook/', payload, format='json', HTTP_X_BOLD_SIGNATURE=signature)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)

    def test_webhook_resolves_order_by_bold_reference(self):
        payment = Payment.objects.create(
            order=self.order,
            amount='100.00',
            currency='COP',
            status=Payment.Status.PENDING,
            bold_reference=f'{self.order.order_number}-retry123',
        )
        payload = {
            'event': 'SALE_APPROVED',
            'transaction_id': 'txn_retry_001',
            'order_reference': payment.bold_reference,
            'amount': 10000,
            'currency': 'COP',
            'timestamp': '2026-05-24T14:30:00Z',
        }

        response = self.client.post(
            '/api/payments/webhook/',
            payload,
            format='json',
            HTTP_X_BOLD_SIGNATURE=self._signature(payload),
        )

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.APPROVED)
        self.assertEqual(payment.transaction_id, 'txn_retry_001')
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)
