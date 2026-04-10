from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiUsuarios.models import Empleado, Usuario


class Stage10UsuariosSecurityTests(APITestCase):
    def setUp(self):
        self.group_admin, _ = Group.objects.get_or_create(name="ADMIN_GENERAL")
        self.group_auditor, _ = Group.objects.get_or_create(name="AUDITOR")

        self.admin = Usuario.objects.create_user(username="stage10_admin_user", password="pass1234")
        self.admin.groups.add(self.group_admin)
        Empleado.objects.create(usuario=self.admin, numero_empleado="EMP-S10-ADM-USR", salario_base=0)

        self.auditor = Usuario.objects.create_user(username="stage10_auditor_user", password="pass1234")
        self.auditor.groups.add(self.group_auditor)
        Empleado.objects.create(usuario=self.auditor, numero_empleado="EMP-S10-AUD-USR", salario_base=0)

    def test_auditor_empleado_no_puede_crear_usuario(self):
        self.client.force_authenticate(self.auditor)
        response = self.client.post(
            "/api/usuarios/",
            {
                "username": "stage10_new_user_forbidden",
                "password": "pass1234",
                "password_confirm": "pass1234",
                "tipo_entidad": "CLIENTE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auditor_capacidades_no_incluyen_admin_general(self):
        self.client.force_authenticate(self.auditor)
        response = self.client.get("/api/usuarios/capacidades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("AUDITOR", response.data["roles"])
        self.assertNotIn("ADMIN_GENERAL", response.data["roles"])
        self.assertFalse(
            any(
                c["resource"] == "user" and c["action"] == "create"
                for c in response.data["capabilities"]
            )
        )
