from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiUsuarios.models import Cliente, Socio, Usuario


class ExternalAccessTests(APITestCase):
    def setUp(self):
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")

        self.cliente_user = Usuario.objects.create_user(username="user_cliente", password="pass1234")
        self.cliente_user.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.cliente_user)

        self.socio_user = Usuario.objects.create_user(username="user_socio", password="pass1234")
        self.socio_user.groups.add(self.group_external)
        Socio.objects.create(usuario=self.socio_user)

    def test_cliente_me_tipo_entidad(self):
        self.client.force_authenticate(user=self.cliente_user)
        response = self.client.get("/api/usuarios/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tipo_entidad"], "CLIENTE")

    def test_socio_me_tipo_entidad(self):
        self.client.force_authenticate(user=self.socio_user)
        response = self.client.get("/api/usuarios/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tipo_entidad"], "SOCIO")

    def test_capacidades_contract_for_external(self):
        self.client.force_authenticate(user=self.cliente_user)
        response = self.client.get("/api/usuarios/capacidades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("USUARIO_EXTERNO", response.data["roles"])
        self.assertTrue(any(item["scope"] == "OWN" for item in response.data["capabilities"]))

    def test_menu_contract_for_external(self):
        self.client.force_authenticate(user=self.cliente_user)
        response = self.client.get("/api/usuarios/menu/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertFalse(any(item["id"] == "auditoria" for item in response.data["items"]))
