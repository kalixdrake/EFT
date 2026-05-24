from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from locations.models import Address, Department, Municipality


PASSWORD = 'StrongPass123!'


def create_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class LocationsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password=PASSWORD,
        )
        self.department = Department.objects.create(name='Antioquia')
        self.municipality = Municipality.objects.create(department=self.department, name='Medellin')

    def test_list_departments_is_public(self):
        response = self.client.get('/api/locations/departments/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_municipalities_filtered_by_department(self):
        response = self.client.get(f'/api/locations/municipalities/?department={self.department.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Medellin')

    def test_create_and_list_user_addresses(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {create_jwt_for_user(self.user)}')
        create_response = self.client.post(
            '/api/locations/addresses/',
            {
                'municipality_id': self.municipality.pk,
                'line': 'Calle 10 # 20-30',
                'label': 'Casa',
                'is_default': True,
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, 201)
        list_response = self.client.get('/api/locations/addresses/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(Address.objects.filter(user=self.user, is_default=True).count(), 1)
