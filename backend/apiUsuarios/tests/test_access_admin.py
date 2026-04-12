from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiUsuarios.models import Empleado, Usuario


class AdminAccessTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.admin = Usuario.objects.create_user(username="user_admin", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-ADM-1", salario_base=0)
        self.client.force_authenticate(user=self.admin)

    def test_me_contract_returns_tipo_entidad(self):
        response = self.client.get("/api/usuarios/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tipo_entidad"], "EMPLEADO")

    def test_admin_can_create_users(self):
        response = self.client.post(
            "/api/usuarios/",
            {
                "username": "nuevo_user",
                "password": "pass1234",
                "password_confirm": "pass1234",
                "tipo_entidad": "CLIENTE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_capacidades_contract_for_admin(self):
        response = self.client.get("/api/usuarios/capacidades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("roles", response.data)
        self.assertIn("ADMIN_GENERAL", response.data["roles"])
        self.assertIn("capabilities", response.data)
        self.assertTrue(any(item["resource"] == "user" for item in response.data["capabilities"]))

    def test_menu_contract_for_admin(self):
        response = self.client.get("/api/usuarios/menu/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertTrue(any(item["id"] == "usuarios" for item in response.data["items"]))
