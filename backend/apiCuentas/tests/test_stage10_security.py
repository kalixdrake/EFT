from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiCuentas.models.cuenta_model import Cuenta
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage10CuentasSecurityTests(APITestCase):
    fixtures = ["json/init_bancos.json", "json/init_cuentas.json"]

    def setUp(self):
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")
        self.group_contabilidad, _ = Group.objects.get_or_create(name="CONTABILIDAD")
        self.group_auditor, _ = Group.objects.get_or_create(name="AUDITOR")

        self.external_user = Usuario.objects.create_user(username="stage10_acc_external", password="pass1234")
        self.external_user.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.external_user)

        self.contabilidad_user = Usuario.objects.create_user(username="stage10_acc_accounting", password="pass1234")
        self.contabilidad_user.groups.add(self.group_contabilidad)
        Empleado.objects.create(usuario=self.contabilidad_user, numero_empleado="EMP-S10-ACC-CNT", salario_base=0)

        self.auditor_user = Usuario.objects.create_user(username="stage10_acc_auditor", password="pass1234")
        self.auditor_user.groups.add(self.group_auditor)
        Empleado.objects.create(usuario=self.auditor_user, numero_empleado="EMP-S10-ACC-AUD", salario_base=0)

        self.cuenta = Cuenta.objects.first()

    def test_externo_no_puede_crear_cuenta(self):
        self.client.force_authenticate(self.external_user)
        response = self.client.post(
            "/api/cuentas/",
            {"banco": self.cuenta.banco_id, "saldo": "100.00", "numero": "S10-NEW", "nombre": "Prueba"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auditor_no_puede_actualizar_cuenta(self):
        self.client.force_authenticate(self.auditor_user)
        response = self.client.patch(f"/api/cuentas/{self.cuenta.id}/", {"saldo": "777.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contabilidad_no_puede_eliminar_cuenta(self):
        self.client.force_authenticate(self.contabilidad_user)
        response = self.client.delete(f"/api/cuentas/{self.cuenta.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
