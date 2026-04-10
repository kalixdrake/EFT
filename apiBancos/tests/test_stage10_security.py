from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apiBancos.models.banco_model import Banco
from apiUsuarios.models import Cliente, Empleado, Usuario


class Stage10BancosSecurityTests(APITestCase):
    fixtures = ["json/init_bancos.json"]

    def setUp(self):
        self.group_external, _ = Group.objects.get_or_create(name="USUARIO_EXTERNO")
        self.group_contabilidad, _ = Group.objects.get_or_create(name="CONTABILIDAD")

        self.external_user = Usuario.objects.create_user(username="stage10_bank_external", password="pass1234")
        self.external_user.groups.add(self.group_external)
        Cliente.objects.create(usuario=self.external_user)

        self.contabilidad_user = Usuario.objects.create_user(username="stage10_bank_accounting", password="pass1234")
        self.contabilidad_user.groups.add(self.group_contabilidad)
        Empleado.objects.create(usuario=self.contabilidad_user, numero_empleado="EMP-S10-BNK-CNT", salario_base=0)

        self.banco = Banco.objects.first()

    def test_externo_no_puede_crear_banco(self):
        self.client.force_authenticate(self.external_user)
        response = self.client.post("/api/bancos/", {"nombre": "Banco Prohibido"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contabilidad_no_puede_eliminar_banco(self):
        self.client.force_authenticate(self.contabilidad_user)
        response = self.client.delete(f"/api/bancos/{self.banco.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
