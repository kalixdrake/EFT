from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient


PASSWORD = 'StrongPass123!'


def create_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class AuthAPITests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='client@example.com',
            email='client@example.com',
            password=PASSWORD,
            first_name='Client',
            last_name='User',
            phone='3001234567',
        )

    def test_register_creates_client_user(self):
        payload = {
            'email': 'new@example.com',
            'password': PASSWORD,
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['email'], 'new@example.com')
        created = self.user_model.objects.get(email='new@example.com')
        self.assertEqual(created.role, 'client')

    def test_login_uses_email_and_returns_tokens(self):
        response = self.client.post('/api/auth/login/', {'email': 'client@example.com', 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_hides_empty_document_fields(self):
        token = create_jwt_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('document_type', response.data)
        self.assertEqual(response.data['phone'], '3001234567')